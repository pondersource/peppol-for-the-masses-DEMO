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

from intuitlib.client import AuthClient
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer


User = get_user_model()

@login_required
def connect(request, template_name='quickbooks/connect.html'):
    auth_client = AuthClient(
            client_id='QBO_CLIENT_ID',
            client_secret='QBO_CLIENT_SECRET',
            environment='sandbox',
            redirect_uri='QBO_REDIRECT_URI',
        )
    client = QuickBooks(
            auth_client=auth_client,
            refresh_token='REFRESH_TOKEN',
            company_id='COMPANY_ID',
        )
    customers = Customer.all(qb=client)
    return render(request, template_name)
