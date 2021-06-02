from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import UserForm

# Create your views here.
def register(response):
    if response.method == "POST":
        form = UserForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
        else:
              return redirect("/register")
    else:
        form = UserForm()

    return render(response,"register/register.html",{"form":form})

def logged(response):
    return render(response , "registration/logged.html",{})
