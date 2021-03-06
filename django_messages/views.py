from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404 , redirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils import timezone
try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.urls import reverse_lazy
from django.conf import settings

from django_messages.models import Message
from django_messages.urls import *
from django_messages.forms import ComposeForm
from django_messages.utils import format_quote, get_user_model, get_username_field
from connection.models import Contact, ConnectionRequest
from peppol.peppol_lib.Sender import *
from django.core.exceptions import ObjectDoesNotExist
from connection.exceptions import AlreadyExistsError
from accounts.models import Activation
from connection.models import bust_cache, cache_key
from django.db.models import Q

User = get_user_model()

if "pinax.notifications" in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from pinax.notifications import models as notification
else:
    notification = None

@login_required
def inbox(request, template_name='django_messages/inbox.html'):
    """
    Displays a list of received messages for the current user.
    Optional Arguments:
        ``template_name``: name of the template to use.
    """
    message_list = Message.objects.inbox_for(request.user)
    connections = Contact.objects.connections(request.user)
    suppliers = Contact.objects.suppliers(request.user)
    costumers = Contact.objects.costumers(request.user)

    ctx ={}
    ctx['message_list'] = message_list
    ctx['connections'] = connections
    ctx['suppliers'] = suppliers
    ctx['costumers'] = costumers

    return render(request, template_name, ctx)

@login_required
def outbox(request, template_name='django_messages/outbox.html'):
    """
    Displays a list of sent messages by the current user.
    Optional arguments:
        ``template_name``: name of the template to use.
    """
    message_list = Message.objects.outbox_for(request.user)
    connections = Contact.objects.connections(request.user)
    costumers = Contact.objects.costumers(request.user)
    suppliers = Contact.objects.suppliers(request.user)

    ctx ={}
    ctx['message_list'] = message_list
    ctx['connections'] = connections
    ctx['suppliers'] = suppliers
    ctx['costumers'] = costumers

    return render(request, template_name, ctx)

@login_required
def costumers(request, template_name='django_messages/costumers.html'):
    """
    Displays a list of messages with costumers
    """
    message_list = Message.objects.all_for(request.user)
    costumers = Contact.objects.costumers(request.user)

    ctx ={}
    ctx['message_list'] = message_list
    ctx['costumers'] = costumers

    return render(request, template_name, ctx)

@login_required
def suppliers(request, template_name='django_messages/suppliers.html'):
    """
    Displays a list of messages with suppliers
    """
    message_list = Message.objects.all_for(request.user)
    suppliers = Contact.objects.suppliers(request.user)

    ctx ={}
    ctx['message_list'] = message_list
    ctx['suppliers'] = suppliers

    return render(request, template_name, ctx)

@login_required
def trash(request, template_name='django_messages/trash.html'):
    """
    Displays a list of deleted messages.
    Optional arguments:
        ``template_name``: name of the template to use
    Hint: A Cron-Job could periodicly clean up old messages, which are deleted
    by sender and recipient.
    """
    message_list = Message.objects.trash_for(request.user)
    return render(request, template_name, {
        'message_list': message_list,
    })

@login_required
def compose(request, recipient=None, form_class=ComposeForm,
        template_name='django_messages/compose.html', success_url=None,
        ):
    """
    Displays and handles the ``form_class`` form to compose new messages.
    Required Arguments: None
    Optional Arguments:
        ``recipient``: username of a `django.contrib.auth` User, who should
                       receive the message
        ``form_class``: the form-class to use
        ``template_name``: the template to use
        ``success_url``: where to redirect after successfull submission

    Passing GET parameter ``subject`` to the view allows pre-filling the
    subject field of the form.
    """

    ctx = {}
    connections = Contact.objects.connections(request.user)

    ctx['connections'] = connections

    priority =[]
    for c in connections:
        priority.append(c)

    priority.append(request.user.username)
    no_connections_objects = User.objects.exclude(username__in=priority)

    for c in no_connections_objects:
        priority.append(c.username)

    form = form_class(initial={"subject": request.GET.get("subject", "")})
    ctx['priority'] = priority
    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST, request.FILES)
        recipient_username_or_webID_or_PeppolID = request.POST['recipient'].split()
        recipient_UWP = recipient_username_or_webID_or_PeppolID[0]
        xml_type = request.POST['xml']
        peppol_classic = request.POST.get('peppol')

        try:
            recipient = Activation.objects.get(webID=recipient_UWP)
            if peppol_classic:
                ctx['form'] = form_class(initial={"subject": request.GET.get("subject", "")})
                messages.info(request, _(u"You can't send a new message to a WEebID through Peppol classic "))
                return render(request, template_name, ctx)
            recipient_username = recipient.user.username
            recipient = User.objects.get(username=recipient_username)
        except ObjectDoesNotExist:
            try:
                recipient = Activation.objects.get(peppolID=recipient_UWP)
                recipient_username = recipient.user.username
                recipient = User.objects.get(username=recipient_username)
            except ObjectDoesNotExist:
                try:
                    recipient = User.objects.get(username=recipient_UWP)
                    recipient_username = recipient.username
                except ObjectDoesNotExist as e:
                    ctx["errors"] = ["%s" % e]
                    return render(request, template_name, ctx )

        if  sender.username == recipient_username:
            messages.info(request, _(u"Why are you talking to yourself?"))
            return render(request, template_name, ctx)

        else:
            if form.is_valid():
                recipient = User.objects.get(pk=recipient.pk)
                form.save(sender=request.user , recipient=recipient , xml_type=xml_type, peppol_classic = peppol_classic)
                messages.info(request, _(u"Message successfully sent."))
                if success_url is None:
                    success_url = reverse_lazy('django_messages:messages_outbox')
                if 'next' in request.GET:
                    success_url = request.GET['next']

                return HttpResponseRedirect(success_url)
    ctx['form'] = form
    return render(request, template_name,ctx)

@login_required
def reply(request, message_id, form_class=ComposeForm,
        template_name='django_messages/compose.html', success_url=None,
        recipient=None, quote_helper=format_quote,
        subject_template=_(u"Re: %(subject)s"),):
    """
    Prepares the ``form_class`` form for writing a reply to a given message
    (specified via ``message_id``). Uses the ``format_quote`` helper from
    ``messages.utils`` to pre-format the quote. To change the quote format
    assign a different ``quote_helper`` kwarg in your url-conf.

    """
    parent = get_object_or_404(Message, id=message_id)

    if parent.sender != request.user and parent.recipient != request.user:
        raise Http404

    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST,request.FILES)
        if form.is_valid():
            form.save(sender=request.user, parent_msg=parent,recipient=parent.sender)
            messages.info(request, _(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse_lazy('django_messages:messages_inbox')
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(initial={
            'body': quote_helper(parent.sender, parent.body),
            'subject': subject_template % {'subject': parent.subject},
            'recipient': [parent.sender,]
            })
    return render(request, template_name, {
        'form': form,
    })

@login_required
def delete(request, message_id, success_url=None):
    """
    Marks a message as deleted by sender or recipient. The message is not
    really removed from the database, because two users must delete a message
    before it's save to remove it completely.
    A cron-job should prune the database and remove old messages which are
    deleted by both users.
    As a side effect, this makes it easy to implement a trash with undelete.

    You can pass ?next=/foo/bar/ via the url to redirect the user to a different
    page (e.g. `/foo/bar/`) than ``success_url`` after deletion of the message.
    """
    user = request.user
    now = timezone.now()
    message = get_object_or_404(Message, id=message_id)
    deleted = False
    if success_url is None:
         success_url = reverse_lazy('django_messages:messages_inbox')
    if 'next' in request.GET:
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = now
        deleted = True
    if message.recipient == user:
        message.recipient_deleted_at = now
        deleted = True
    if deleted:
        message.save()
        messages.info(request, _(u"Message successfully deleted."))
        if notification:
            notification.send([user], "messages_deleted", {'message': message,})
        return HttpResponseRedirect(success_url)
    raise Http404

@login_required
def undelete(request, message_id, success_url=None):
    """
    Recovers a message from trash. This is achieved by removing the
    ``(sender|recipient)_deleted_at`` from the model.
    """
    user = request.user
    message = get_object_or_404(Message, id=message_id)
    undeleted = False
    if success_url is None:
        success_url = reverse_lazy('django_messages:messages_inbox')
    if 'next' in request.GET:
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = None
        undeleted = True
    if message.recipient == user:
        message.recipient_deleted_at = None
        undeleted = True
    if undeleted:
        message.save()
        messages.info(request, _(u"Message successfully recovered."))
        if notification:
            notification.send([user], "messages_recovered", {'message': message,})
        return HttpResponseRedirect(success_url)
    raise Http404

@login_required
def view(request, message_id, form_class=ComposeForm, quote_helper=format_quote,
        subject_template=_(u"Re: %(subject)s"),
        template_name='django_messages/view.html'):
    """
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either
    the sender or the recipient. If the user is not allowed a 404
    is raised.
    If the user is the recipient and the message is unread
    ``read_at`` is set to the current datetime.
    If the user is the recipient a reply form will be added to the
    tenplate ctx, otherwise 'reply_form' will be None.
    """

    user = request.user
    now = timezone.now()
    connections = Contact.objects.connections(request.user)
    suppliers = Contact.objects.suppliers(request.user)
    costumers = Contact.objects.costumers(request.user)

    message = get_object_or_404(Message, id=message_id)

    if (message.sender != user) and (message.recipient != user):
        raise Http404
    if message.read_at is None and message.recipient == user:
        message.read_at = now
        message.save()

    ctx = {'message': message, 'reply_form': None , 'connections': connections , 'suppliers' : suppliers , 'costumers' : costumers }

    if message.recipient == user:
        form = form_class(initial={
            'body': quote_helper(message.sender, message.body),
            'subject': subject_template % {'subject': message.subject},
            'recipient': [message.sender,]
            })
        ctx['reply_form'] = form

    if request.method == "POST":

        accept = request.POST.get('accept')
        username = request.POST.get('username')
        accept = True
        # Get Contact

        if accept:
            try:
                partner = User.objects.get(username = username)
            except ObjectDoesNotExist as e:
                ctx["erros"] = ["%s" % e]
                return render(request, template_name, ctx)

        # if users are not connected, connect them
            if Contact.objects.are_connections(request.user, partner):
                pass
            elif ConnectionRequest.objects.filter(Q(to_user=request.user, from_user = partner) | Q(to_user= partner, from_user=request.user)).exists():
                ConnectionRequest.objects.get(Q(to_user=request.user, from_user= partner) | Q(to_user= partner, from_user=request.user)).accept()
            else:
                try:
                    Contact.objects.add_connection( partner, request.user).accept()
                except AlreadyExistsError:
                    pass

            contact = Contact.objects.get(to_user = partner , from_user = request.user )
            reverse_contact = Contact.objects.get(to_user = request.user , from_user = partner )

            if message.xml_type == 'invoice':
                contact.is_supplier = True
                reverse_contact.is_costumer = True

            elif message.xml_type == 'purchase':
                contact.is_costumer = True
                reverse_contact.is_supplier = True

        contact.save()
        reverse_contact.save()
        return redirect('django_messages:messages_detail', message_id=message.id )

    return render(request, template_name, ctx)

def review(request, message_id, template_name = 'django_messages/review.html'):

    return render(request, template_name, )
