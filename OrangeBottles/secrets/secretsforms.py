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

class createBlackmailForm(forms.Form):
    target = forms.EmailField(max_length=50)
    picture = forms.ImageField()
    deadline = forms.DateTimeField()
    term1 = forms.CharField(max_length=400, required=True, label="First demand")
    term2 = forms.CharField(max_length=400, required=False, label="Second demand (Optional)")
    term3 = forms.CharField(max_length=400, required=False, label="Third demand (Optional)")

class createEditForm(forms.Form):
    picture = forms.ImageField()
    deadline = forms.DateTimeField()
    term1 = forms.CharField(max_length=400, required=True, label="First demand")
    term2 = forms.CharField(max_length=400, required=False, label="Second demand (Optional)")
    term3 = forms.CharField(max_length=400, required=False, label="Third demand (Optional)")

class editUserForm(forms.Form):
    Name = forms.CharField(max_length=30, required=True)
    Email = forms.EmailField(required=True)
    oldPassword = forms.CharField(widget=forms.PasswordInput, required=True, label="enter your current password")
    Password = forms.CharField(widget=forms.PasswordInput, required=False, label="enter your new password")
    RePassword = forms.CharField(widget=forms.PasswordInput, required=False, label="Re-type your new password")
