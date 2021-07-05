from django.conf.urls import re_path
from django.views.generic import RedirectView

from quickbooks.views import *

app_name = 'quickbooks'

urlpatterns = [
    re_path(r'^$', connect, name='quickbooks_connect'),
]
