from django.forms import ModelForm
from django import forms
from models import BlackmailFields

class loginForm(forms.Form):
    Email = forms.EmailField()
    Password = forms.CharField(widget=forms.PasswordInput)

class createUserForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Password = forms.CharField(widget=forms.PasswordInput)
    RePassword = forms.CharField(widget=forms.PasswordInput, label="Re-type your password")

class createBlackmailForm(ModelForm):
    class Meta:
        model = BlackmailFields

class createEditForm(ModelForm):
    class Meta:
        model = BlackmailFields
