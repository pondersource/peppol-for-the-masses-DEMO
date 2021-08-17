from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

if "pinax.notifications" in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from pinax.notifications import models as notification
else:
    notification = None

from django_messages.models import Message , MessageManager

from django_messages.utils import get_user_model
from connection.views import get_connection_context_object_list_name
from connection.models import Contact
from connection.exceptions import AlreadyExistsError

from django.contrib.auth.models import User
from connection.models import Contact, ConnectionManager , ConnectionRequest

try:
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

    user_model = User


def my_username(request):
    username = None
    if request.user.is_authenticated():
        username = request.user.username

def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.xml']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension. (Accepts only XML files)')

class ComposeForm(forms.Form):
    """
    A simple default form for private messages.

    """

    subject = forms.CharField( max_length=140)
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}),label='Message')
    invoice = forms.FileField(
        label='XML Upload:',
        required=False,
        validators=[validate_file_extension]
    )

    def save(self, sender, recipient, xml_type , parent_msg=None ,):
        recipient = recipient
        xml_type = xml_type
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        invoice = self.cleaned_data['invoice']
        message_list = []

        msg = Message(
            sender = sender,
            recipient = recipient,
            subject = subject,
            body = body,
            invoice = invoice,
            xml_type = xml_type
        )
        try:
            Contact.objects.add_connection(sender, recipient)
        except AlreadyExistsError:
            pass
        if parent_msg is not None:
            msg.parent_msg = parent_msg
            parent_msg.replied_at = timezone.now()
            parent_msg.save()
        msg.save()
        message_list.append(msg)
        if notification:
            if parent_msg is not None:
                notification.send([sender], "messages_replied", {'message': msg,})
                notification.send([recipient], "messages_reply_received", {'message': msg,})
            else:
                notification.send([sender], "messages_sent", {'message': msg,})
                notification.send([recipient], "messages_received", {'message': msg,})
        return message_list
