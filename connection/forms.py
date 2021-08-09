
from django import forms
from django.contrib.auth.models import User

# creating a form
class  FindUserForm(forms.Form):
    user= forms.ModelChoiceField(queryset=User.objects.all(),empty_label='PonderSourse')
