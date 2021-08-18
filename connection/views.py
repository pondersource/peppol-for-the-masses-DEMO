from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect

from connection.exceptions import AlreadyExistsError , ValidationError
from django.core.exceptions import ObjectDoesNotExist
from connection.models import Block, Follow, Contact, ConnectionRequest
from django.views.generic import TemplateView
from django import forms
from django.contrib.auth.models import User
try:
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

    user_model = User

from accounts.models import Activation

def get_connection_context_object_name():
    return getattr(settings, "CONNECTION_CONTEXT_OBJECT_NAME", "user")


def get_connection_context_object_list_name():
    return getattr(settings, "CONNECTION_CONTEXT_OBJECT_LIST_NAME", "users")

def view_connections(request, username, template_name="connection/connection/user_list.html"):
    """ View the connections of a user """

    connections = Contact.objects.connections(request.user)
    suppliers = Contact.objects.suppliers(request.user)

    ctx ={ 'connections' : connections , 'suppliers' : suppliers }
    return render(request,template_name, ctx)


@login_required
def connection_add_connection(
    request, template_name="connection/connection/add.html"
):
    """ Create a ConnectionRequest """

    users = User.objects.exclude(username=request.user)
    ctx = {}
    ctx['users'] = users
    if request.method == "POST":
        username_or_WebId = request.POST['username_or_WebId']
        try:
            to_user = Activation.objects.get(webID=username_or_WebId)
        except ObjectDoesNotExist as e:
            try:
                to_user = User.objects.get(username=username_or_WebId)
            except ObjectDoesNotExist as e:
                ctx["errors"] = ["%s" % e]
                return render(request, template_name, ctx )
        to_user = User.objects.get(pk=to_user.pk)
        from_user = request.user
        try:
            Contact.objects.add_connection(from_user, to_user)
        except AlreadyExistsError as e:
            ctx["errors"] = ["%s" % e]
            return render(request, template_name, ctx )

        else:
            return redirect("connection:connection_requests_sent")
    return render(request, template_name, ctx)

@login_required
def connection_accept(request, connection_request_id):
    """ Accept a connection request """
    f_request = get_object_or_404(
        request.user.connection_requests_received, id=connection_request_id
    )
    f_request.accept()
    return redirect("connection:connection_view_connections", username=request.user.username)


@login_required
def connection_reject(request, connection_request_id):
    """ Reject a connection request """
    f_request = get_object_or_404(
        request.user.connection_requests_received, id=connection_request_id
    )
    f_request.reject()
    return redirect("connection:connection_request_list")


@login_required
def connection_cancel(request, connection_request_id):
    """ Cancel a previously created connection_request_id """
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.connection_requests_sent, id=connection_request_id
        )
        f_request.cancel()
        return redirect("connection:connection_requests_sent")

    return redirect("connection:connection_requests_sent")


@login_required
def connection_request_list(
    request, template_name="connection/connection/requests_list.html"
):
    """ View unread and read connection requests """
    # This shows all connection requests in the database
    connection_requests = ConnectionRequest.objects.filter(rejected__isnull=True)
    for q in connection_requests:
        q.mark_viewed()

    return render(request, template_name, {"requests": connection_requests})


@login_required
def connection_request_list_rejected(
    request, template_name="connection/connection/requests_list.html"
):
    """ View rejected connection requests """
    # connection_requests = Contact.objects.rejected_requests(request.user)
    connection_requests = ConnectionRequest.objects.filter(rejected__isnull=False)

    return render(request, template_name, {"requests": connection_requests})


@login_required
def connection_requests_sent(
    request, template_name="connection/connection/sent_requests.html"
):
    """ View all the sent connection requests from a user"""
    sent_requests= Contact.objects.sent_requests(request.user)

    return render(request, template_name, {"sent_requests": sent_requests})

def blocking(request, username, template_name="connection/block/blockers_list.html"):
    """ List this user's followers """
    user = get_object_or_404(user_model, username=username)
    Block.objects.blocked(user)

    return render(
        request,
        template_name,
        {
            get_connection_context_object_name(): user,
            "connection_context_object_name": get_connection_context_object_name(),
        },
    )


def blockers(request, username, template_name="connection/block/blocking_list.html"):
    """ List who this user follows """
    user = get_object_or_404(user_model, username=username)
    Block.objects.blocking(user)

    return render(
        request,
        template_name,
        {
            get_connection_context_object_name(): user,
            "connection_context_object_name": get_connection_context_object_name(),
        },
    )


@login_required
def block_add(request, blocked_username, template_name="connection/block/add.html"):
    """ Create a following relationship """
    ctx = {"blocked_username": blocked_username}

    if request.method == "POST":
        blocked = user_model.objects.get(username=blocked_username)
        blocker = request.user
        try:
            Block.objects.add_block(blocker, blocked)
        except AlreadyExistsError as e:
            ctx["errors"] = ["%s" % e]
        else:
            return redirect("connection:connection_blocking", username=blocker.username)

    return render(request, template_name, ctx)


@login_required
def block_remove(request, blocked_username):
    """ Remove a following relationship """
    #if request.method == "POST":
    blocked = user_model.objects.get(username=blocked_username)
    blocker = request.user
    Block.objects.remove_block(blocker, blocked)
    return redirect("connection:connection_blocking", username=blocker.username)

    #return render(request, template_name, {"blocked_username": blocked_username})

@login_required
def connection_remove(request, connection_to_remove):
    """ Remove a connection"""
    connection_to_remove = user_model.objects.get(username=connection_to_remove)
    remover = request.user
    Contact.objects.remove_connection(remover,connection_to_remove)
    return redirect("connection:connection_view_connections" , username=remover.username)

@login_required
def supplier_remove(request, supplier_to_remove):
    """ Remove a supplier"""
    supplier_to_remove = user_model.objects.get(username=supplier_to_remove)
    remover = request.user
    Contact.objects.remove_supplier(remover,supplier_to_remove)
    return redirect("connection:connection_view_connections" , username=remover.username)

@login_required
def costumer_remove(request, costumer_to_remove):
    """ Remove a costumer"""
    costumer_to_remove = user_model.objects.get(username=costumer_to_remove)
    remover = request.user
    Contact.objects.remove_supplier(remover,costumer_to_remove)
    return redirect("connection:connection_view_connections" , username=remover.username)
