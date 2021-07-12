from django.conf.urls import re_path
from connection.views import (
    all_users,
    block_add,
    block_remove,
    blockers,
    blocking,
    connection_accept,
    connection_add_connection,
    connection_cancel,
    connection_reject,
    connection_remove,
    connection_request_list,
    connection_request_list_rejected,
    connection_requests_detail,
    view_connections,
    contacts
)

app_name = 'connection'

urlpatterns = [
    re_path(r"^users/$", view=all_users, name="connection_view_users"),
    re_path(
        r"^connections/(?P<username>[\w-]+)/$",
        view=view_connections,
        name="connection_view_connections",
    ),
    re_path(
        r"^connection/add/(?P<to_username>[\w-]+)/$",
        view=connection_add_connection,
        name="connection_add_connection",
    ),
    re_path(
        r"^connection/accept/(?P<connection_request_id>\d+)/$",
        view=connection_accept,
        name="connection_accept",
    ),
    re_path(
        r"^connection/reject/(?P<connection_request_id>\d+)/$",
        view=connection_reject,
        name="connection_reject",
    ),
    re_path(
        r"^connection/cancel/(?P<connection_request_id>\d+)/$",
        view=connection_cancel,
        name="connection_cancel",
    ),
    re_path(
        r"^connection/requests/$",
        view=connection_request_list,
        name="connection_request_list",
    ),
    re_path(
        r"^connection/requests/rejected/$",
        view=connection_request_list_rejected,
        name="connection_requests_rejected",
    ),
    re_path(
        r"^connection/request/(?P<connection_request_id>\d+)/$",
        view=connection_requests_detail,
        name="connection_requests_detail",
    ),
    re_path(
        r"^connection/remove/(?P<connection_to_remove>[\w-]+)/$",
        view=connection_remove,
        name="connection_remove",
    ),
    re_path(
        r"^blockers/(?P<username>[\w-]+)/$",
        view=blockers,
        name="connection_blockers",
    ),
    re_path(
        r"^blocking/(?P<username>[\w-]+)/$",
        view=blocking,
        name="connection_blocking",
    ),
    re_path(
        r"^block/add/(?P<blocked_username>[\w-]+)/$",
        view=block_add,
        name="block_add",
    ),
    re_path(
        r"^block/remove/(?P<blocked_username>[\w-]+)/$",
        view=block_remove,
        name="block_remove",
    ),

    re_path(r"^contacts/$",
    view=contacts,
    name="contacts")
]
