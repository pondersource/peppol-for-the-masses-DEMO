from __future__ import absolute_import, print_function

from requests import HTTPError
import json
import sys

from intuitlib.client import AuthClient
from intuitlib.migration import migrate
from intuitlib.utils import send_request
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.conf import settings
from django.core import serializers


from django.contrib.auth.models import User
from django_messages.models import Message

from quickbooks.services import qbo_query

# Create your views here.
def index(request):
    return render(request, 'quickbooks/index.html')

def oauth(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT,
    )

    url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
    request.session['state'] = auth_client.state_token
    return redirect(url)

def openid(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT,
    )

    url = auth_client.get_authorization_url([Scopes.OPENID, Scopes.EMAIL])
    request.session['state'] = auth_client.state_token
    return redirect(url)

def callback(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        state_token=request.session.get('state', None),
    )

    state_tok = request.GET.get('state', None)
    error = request.GET.get('error', None)
    
    if error == 'access_denied':
        return redirect('quickbooks:index')
    
    if state_tok is None:
        return HttpResponseBadRequest()
    elif state_tok != auth_client.state_token:  
        return HttpResponse('unauthorized', status=401)
    
    auth_code = request.GET.get('code', None)
    realm_id = request.GET.get('realmId', None)
    request.session['realm_id'] = realm_id

    if auth_code is None:
        return HttpResponseBadRequest()

    try:
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        request.session['access_token'] = auth_client.access_token
        request.session['refresh_token'] = auth_client.refresh_token
        request.session['id_token'] = auth_client.id_token
    except AuthClientError as e:
        # just printing status_code here but it can be used for retry workflows, etc
        print(e.status_code)
        print(e.content)
        print(e.intuit_tid)
    except Exception as e:
        print(e)
    return redirect('quickbooks:connected')

def connected(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
        id_token=request.session.get('id_token', None),
    )

    if auth_client.id_token is not None:
        return render(request, 'quickbooks/connected.html', context={'openid': True})
    else:
        return render(request, 'quickbooks/connected.html', context={'openid': False})

def qbo_request(request, table):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
        realm_id=request.session.get('realm_id', None),
    )

    if auth_client.access_token is not None:
        access_token = auth_client.access_token

    if auth_client.realm_id is None:
        raise ValueError('Realm id not specified.')
    response = qbo_query(auth_client.access_token, auth_client.realm_id, table)
    
    if not response.ok:
        print("not ok", file=sys.stderr)
        return ' '.join([response.content, str(response.status_code)])
    else:
        print("yes ok", file=sys.stderr)
        return json.loads(response.content)

def display(arr, table, field):
    str = "imported " + table + "! <ul>"
    for i in arr:
        print("i!! %s", i, file=sys.stderr)
        str += "<li>" + i[field] + "</li>"
    return HttpResponse(str + "</ul>")

def invoiceToString(invoice):
    # return str(invoice["DocNumber"]) + ": Please pay " + str(invoice["Balance"]) + " by " + str(invoice["DueDate"])
    return str("-") + ": Please pay " + str(invoice["Balance"]) + " by " + str(invoice["DueDate"])

def ensureInvoice(fromUser, toUser, body):
    print("Ensure Invoice %s %s", fromUser, toUser, body, file=sys.stderr)
    try:
        existingMessage = Message.objects.get(sender=fromUser, recipient=toUser, body=body)
        print("Message exists!", file=sys.stderr)
        return existingMessage
    except Message.DoesNotExist:
        created = Message.objects.create(sender=fromUser, recipient=toUser, body=body)
        print("Created message!", file=sys.stderr)
        return created

def ensureUser(name):
    try:
        existingUser = User.objects.get(username=name)
        print("User exists! " + name, file=sys.stderr)
        return existingUser
    except User.DoesNotExist:
        created = User.objects.create_user(name)
        print("Created user! " + name, file=sys.stderr)
        return created

def display2(arr, table, field1, field2):
    str = "imported " + table + "! <ul>"
    for i in arr:
        print("i!! %s", i, file=sys.stderr)
        str += "<li>" + i[field1][field2] + "</li>"
    return HttpResponse(str + "</ul>")

def qbo_suppliers(request):
    suppliers = qbo_request(request, 'vendor')["QueryResponse"]["Vendor"]
    for i in suppliers:
        ensureUser(i["DisplayName"])
    return display(suppliers, "suppliers", "DisplayName")

def qbo_invoices_received(request):
    bills = qbo_request(request, 'bill')["QueryResponse"]["Bill"]
    for i in bills:
        vendorUser = ensureUser(i["VendorRef"]["name"])
        ensureInvoice(vendorUser, request.user, invoiceToString(i))
    return display2(bills, "invoices recceived", "VendorRef", "name")

def qbo_customers(request):
    customers = qbo_request(request, 'customer')["QueryResponse"]["Customer"]
    for i in customers:
        ensureUser(i["DisplayName"])
    return display(customers, "customers", "DisplayName")

def qbo_invoices_sent(request):
    invoices = qbo_request(request, 'invoice')["QueryResponse"]["Invoice"]
    for i in invoices:
        customerUser = ensureUser(i["CustomerRef"]["name"])
        ensureInvoice(request.user, customerUser, invoiceToString(i))
    return display2(invoices, "invoices sent", "CustomerRef", "name")

def user_info(request):
    print("hi", file=sys.stderr)
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
        id_token=request.session.get('id_token', None),
    )

    try:
        # response = auth_client.get_user_info()
        token = auth_client.access_token
        if token is None:
            raise ValueError('Acceess token not specified')

        headers = {
            'Authorization': 'Bearer {0}'.format(token)
        }
        print("Requesting %s", auth_client.user_info_url, file=sys.stderr)
        response = send_request('GET', auth_client.user_info_url, headers, auth_client, session=auth_client)
    except ValueError:
        return HttpResponse('id_token or access_token not found.')
    except AuthClientError as e:
        print(e.status_code)
        print(e.intuit_tid)
    return HttpResponse(response.content)
        
def refresh(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
    )

    try:
        auth_client.refresh() 
    except AuthClientError as e:
        print(e.status_code)
        print(e.intuit_tid)
    return HttpResponse('New refresh_token: {0}'.format(auth_client.refresh_token))

def revoke(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
    )
    try:
        is_revoked = auth_client.revoke()
    except AuthClientError as e:
        print(e.status_code)
        print(e.intuit_tid)
    return HttpResponse('Revoke successful')


def migration(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT,
    )
    try:
        migrate(
            settings.CONSUMER_KEY, 
            settings.CONSUMER_SECRET, 
            settings.ACCESS_KEY, 
            settings.ACCESS_SECRET, 
            auth_client, 
            [Scopes.ACCOUNTING]
        )
    except AuthClientError as e:
        print(e.status_code)
        print(e.intuit_tid)
    return HttpResponse('OAuth2 refresh_token {0}'.format(auth_client.refresh_token))
