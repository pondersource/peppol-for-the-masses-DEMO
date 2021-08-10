
from django import forms
from django.contrib.auth.models import User

# creating a form
class  FindUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True),empty_label='PonderSourse')
