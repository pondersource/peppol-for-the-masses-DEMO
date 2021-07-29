from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

if "pinax.notifications" in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from pinax.notifications import models as notification
else:
    notification = None

from django_messages.models import Message , MessageManager
from django_messages.fields import CommaSeparatedUserField

from django_messages.utils import get_user_model
from connection.views import get_connection_context_object_list_name
from connection.models import Contact

from django.contrib.auth.models import User
from connection.models import Contact, ConnectionManager

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

    # users = forms.ModelChoiceField(
    #     queryset = Users,
    #     initial = 0
    #     )

    recipient = CommaSeparatedUserField()
    subject = forms.CharField( max_length=140)
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}),label='Message')
    invoice = forms.FileField(
        label='XML File Upload:',
        required=False,
        validators=[validate_file_extension]
    )

    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop('recipient_filter', None)
        super(ComposeForm, self).__init__(*args, **kwargs)
        if recipient_filter is not None:
            self.fields['recipient']._recipient_filter = recipient_filter



    def save(self, sender, parent_msg=None):
        recipients = self.cleaned_data['recipient']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        invoice = self.cleaned_data['invoice']
        message_list = []
        for r in recipients:
            msg = Message(
                sender = sender,
                recipient = r,
                subject = subject,
                body = body,
                invoice = invoice,
            )
            if not ConnectionManager.are_connections(self, sender, r):
                to_user = user_model.objects.get(username=r.username)
                from_user = sender
                Contact.objects.add_connection(from_user, to_user)

            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = timezone.now()
                parent_msg.save()
            msg.save()
            message_list.append(msg)
            if notification:
                if parent_msg is not None:
                    notification.send([sender], "messages_replied", {'message': msg,})
                    notification.send([r], "messages_reply_received", {'message': msg,})
                else:
                    notification.send([sender], "messages_sent", {'message': msg,})
                    notification.send([r], "messages_received", {'message': msg,})
        return message_list
