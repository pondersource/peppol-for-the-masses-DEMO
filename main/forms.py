from django import forms

class CreateNewList(forms.Form):
    name = forms.CharField(label="Username",max_length=200)
