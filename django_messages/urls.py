from django.conf.urls import re_path
from django.views.generic import RedirectView

from django_messages.views import *

app_name = 'django_messages'


urlpatterns = [
    re_path(r'^$',
            RedirectView.as_view(permanent=True,
            url='inbox/'),
            name='messages_redirect'),

    re_path(r'^inbox/$',
            inbox,
            name='messages_inbox'),

    re_path(r'^outbox/$',
            outbox,
            name='messages_outbox'),

    re_path(r'^compose/$',
            compose,
            name='messages_compose'),

    re_path(r'^compose/(?P<recipient>[\w.@+-]+)/$',
            compose,
            name='messages_compose_to'),

    re_path(r'^reply/(?P<message_id>[\d]+)/$',
            reply,
            name='messages_reply'),

    re_path(r'^view/(?P<message_id>[\d]+)/$',
            view,
            name='messages_detail'),

    re_path(r'^delete/(?P<message_id>[\d]+)/$',
            delete,
            name='messages_delete'),

    re_path(r'^undelete/(?P<message_id>[\d]+)/$',
            undelete,
            name='messages_undelete'),

    re_path(r'^trash/$',
            trash,
            name='messages_trash'),

    re_path(r'^review/(?P<message_id>[\d]+)/$',
            review,
            name='messages_review'),

]
