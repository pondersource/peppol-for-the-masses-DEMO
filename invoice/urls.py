from django.urls import path
from . import views

urlpatterns = [
    path("invoiceSend/",views.invoice , name="invoiceSend"),
    path("invoice/",views.invoice,name="invoice"),
]
