from django import forms

class loginForm(forms.Form):
    Email = forms.EmailField()
    Password = forms.CharField(widget=forms.PasswordInput)
