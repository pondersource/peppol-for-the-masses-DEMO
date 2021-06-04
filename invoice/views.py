from django.shortcuts import render, redirect
from .forms import InvoiceForm
from django.http import HttpResponseRedirect

# Create your views here.
def invoice(response):
    if response.method == "POST":
        form = InvoiceForm(response.POST)
        if form.is_valid():
            form.save()
            return render(response , "invoice/invoiceSend.html",{})
        else:
              return render(response , "invoice/invoice.html",{})
    else:
        form = InvoiceForm()
    return render(response , "invoice/invoice.html",{"form":form})
