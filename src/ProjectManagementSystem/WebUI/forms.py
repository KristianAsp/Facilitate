from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import re

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    username.widget.attrs.update({'class' : 'form-control'})
    username.widget.attrs.update({'placeholder' : 'Username'})

    password = forms.CharField(widget = forms.PasswordInput())
    password.widget.attrs.update({'class' : 'form-control'})
    password.widget.attrs.update({'placeholder' : 'Password'})

    def clean_password(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        user = authenticate(username = username, password = password)
        if not user:
            raise forms.ValidationError("Incorrect username or password.")
        return username

class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=100)
    username.widget.attrs.update({'class' : 'form-control'})
    username.widget.attrs.update({'placeholder' : 'Username'})

    email = forms.EmailField()
    email.widget.attrs.update({'class' : 'form-control'})
    email.widget.attrs.update({'placeholder' : 'Email'})

    password = forms.CharField(widget = forms.PasswordInput())
    password.widget.attrs.update({'class' : 'form-control'})
    password.widget.attrs.update({'placeholder' : 'Password'})

    confirm_password = forms.CharField(widget = forms.PasswordInput())
    confirm_password.widget.attrs.update({'class' : 'form-control'})
    confirm_password.widget.attrs.update({'placeholder' : 'Confirm password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)

    def clean_confirm_password(self):
        PASSWORD_REGEX_PATTERN = "^([a-zA-Z0-9]+)+$"
        pattern = re.compile(PASSWORD_REGEX_PATTERN)
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]

        if not pattern.match(password):
            raise forms.ValidationError("A password can only contain letters from A-Z and digits.")

        if password != confirm_password:
            raise forms.ValidationError("The passwords do not match")

class NewProjectForm(forms.Form):
    project_title = forms.CharField(max_length=100)
    project_title.widget.attrs.update({'class' : 'form-control'})

    description = forms.CharField(max_length=100)
    description.widget.attrs.update({'class' : 'form-control'})
