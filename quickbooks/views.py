from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils import timezone
from django.urls import reverse_lazy
from django.conf import settings

from django_messages.models import Message
from django_messages.urls import *
from django_messages.forms import ComposeForm
from django_messages.utils import format_quote, get_user_model, get_username_field

User = get_user_model()

@login_required
def connect(request, template_name='quickbooks/connect.html'):
    return render(request, template_name)
