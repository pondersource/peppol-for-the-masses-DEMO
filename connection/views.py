from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from connection.exceptions import AlreadyExistsError
from connection.models import Block, Follow, Contact, ConnectionRequest

try:
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

    user_model = User

def get_connection_context_object_name():
    return getattr(settings, "CONNECTION_CONTEXT_OBJECT_NAME", "user")


def get_connection_context_object_list_name():
    return getattr(settings, "CONNECTION_CONTEXT_OBJECT_LIST_NAME", "users")


def view_connections(request, username, template_name="connection/connection/user_list.html"):
    """ View the connections of a user """
    user = get_object_or_404(user_model, username=username)
    connections = Contact.objects.connections(user)
    return render(
        request,
        template_name,
        {
            get_connection_context_object_name(): user,
            "connection_context_object_name": get_connection_context_object_name(),
            "connections": connections,
        },
    )


@login_required
def connection_add_connection(
    request, to_username, template_name="connection/connection/add.html"
):
    """ Create a ConnectionRequest """
    ctx = {"to_username": to_username}

    if request.method == "POST":
        to_user = user_model.objects.get(username=to_username)
        from_user = request.user
        try:
            Contact.objects.add_connection(from_user, to_user)
        except AlreadyExistsError as e:
            ctx["errors"] = ["%s" % e]
        else:
            return redirect("connection_request_list")

    return render(request, template_name, ctx)


@login_required
def connection_accept(request, connection_request_id):
    """ Accept a connection request """
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.connection_requests_received, id=connection_request_id
        )
        f_request.accept()
        return redirect("connection_view_connections", username=request.user.username)

    return redirect(
        "connection_requests_detail", connection_request_id=connection_request_id
    )


@login_required
def connection_reject(request, connection_request_id):
    """ Reject a connection request """
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.connection_requests_received, id=connection_request_id
        )
        f_request.reject()
        return redirect("connection_request_list")

    return redirect(
        "connection_requests_detail", connection_request_id=connection_request_id
    )


@login_required
def connection_cancel(request, connection_request_id):
    """ Cancel a previously created connection_request_id """
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.connection_requests_sent, id=connection_request_id
        )
        f_request.cancel()
        return redirect("connection_request_list")

    return redirect(
        "connection_requests_detail", connection_request_id=connection_request_id
    )


@login_required
def connection_request_list(
    request, template_name="connection/connection/requests_list.html"
):
    """ View unread and read connection requests """
    connection_requests = Contact.objects.requests(request.user)
    # This shows all connection requests in the database
    # connection_requests = ConnectionRequest.objects.filter(rejected__isnull=True)

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
def connection_requests_detail(
    request, connection_request_id, template_name="connection/connection/request.html"
):
    """ View a particular connection request """
    f_request = get_object_or_404(ConnectionRequest, id=connection_request_id)

    return render(request, template_name, {"connection_request": f_request})


def followers(request, username, template_name="connection/follow/followers_list.html"):
    """ List this user's followers """
    user = get_object_or_404(user_model, username=username)
    followers = Follow.objects.followers(user)
    return render(
        request,
        template_name,
        {
            get_connection_context_object_name(): user,
            "connection_context_object_name": get_connection_context_object_name(),
            "followers": followers,
        },
    )


def following(request, username, template_name="connection/follow/following_list.html"):
    """ List who this user follows """
    user = get_object_or_404(user_model, username=username)
    following = Follow.objects.following(user)
    return render(
        request,
        template_name,
        {
            get_connection_context_object_name(): user,
            "connection_context_object_name": get_connection_context_object_name(),
            "following": following,
        },
    )


@login_required
def follower_add(
    request, followee_username, template_name="connection/follow/add.html"
):
    """ Create a following relationship """
    ctx = {"followee_username": followee_username}

    if request.method == "POST":
        followee = user_model.objects.get(username=followee_username)
        follower = request.user
        try:
            Follow.objects.add_follower(follower, followee)
        except AlreadyExistsError as e:
            ctx["errors"] = ["%s" % e]
        else:
            return redirect("connection_following", username=follower.username)

    return render(request, template_name, ctx)


@login_required
def follower_remove(
    request, followee_username, template_name="connection/follow/remove.html"
):
    """ Remove a following relationship """
    if request.method == "POST":
        followee = user_model.objects.get(username=followee_username)
        follower = request.user
        Follow.objects.remove_follower(follower, followee)
        return redirect("connection_following", username=follower.username)

    return render(request, template_name, {"followee_username": followee_username})


def all_users(request, template_name="connection/user_actions.html"):
    users = user_model.objects.all()

    return render(
        request, template_name, {get_connection_context_object_list_name(): users}
    )


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
            return redirect("connection_blocking", username=blocker.username)

    return render(request, template_name, ctx)


@login_required
def block_remove(
    request, blocked_username, template_name="connection/block/remove.html"
):
    """ Remove a following relationship """
    if request.method == "POST":
        blocked = user_model.objects.get(username=blocked_username)
        blocker = request.user
        Block.objects.remove_block(blocker, blocked)
        return redirect("connection_blocking", username=blocker.username)

    return render(request, template_name, {"blocked_username": blocked_username})
