from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from WebAPI.choices import *
from WebAPI.models import *
import re
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _



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

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'short_name', 'visibility']

    name = forms.CharField(max_length=100)
    name.widget.attrs.update({'class' : 'form-control'})

    short_name = forms.CharField(max_length=100)
    short_name.widget.attrs.update({'class' : 'form-control'})

class NewTicketForm(forms.Form):
    name = forms.CharField(max_length=100, required = True)
    name.widget.attrs.update({'class' : 'form-control'})

    priority = forms.ChoiceField(choices = PRIORITY_CHOICES, widget = forms.Select(), required = True, initial ='')
    priority.widget.attrs.update({'class' : 'form-control'})

    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5,}), max_length=3000, required = False)
    description.widget.attrs.update({'class' : 'form-control'})

    type = forms.ChoiceField(choices = TYPE_CHOICES, widget = forms.Select(), required = True, initial ='' )
    type.widget.attrs.update({'class' : 'form-control'})

    assigned_to = forms.CharField(max_length=100, required = False)
    assigned_to.widget.attrs.update({'class' : 'form-control assigned_to', 'id' : 'assigned_to'})


class ProfileForm(forms.Form):
    username = forms.CharField(max_length=100)
    username.widget.attrs.update({'class' : 'form-control'})

    first_name = forms.CharField(max_length=100)
    first_name.widget.attrs.update({'class' : 'form-control'})

    last_name = forms.CharField(max_length=100)
    last_name.widget.attrs.update({'class' : 'form-control'})

    email = forms.EmailField()
    email.widget.attrs.update({'class' : 'form-control'})

    current_password = forms.CharField(widget = forms.PasswordInput())
    current_password.widget.attrs.update({'class' : 'form-control'})
    current_password.widget.attrs.update({'placeholder' : '********'})

    password = forms.CharField(widget = forms.PasswordInput())
    password.widget.attrs.update({'class' : 'form-control'})
    password.widget.attrs.update({'placeholder' : '********'})

    confirm_password = forms.CharField(widget = forms.PasswordInput())
    confirm_password.widget.attrs.update({'class' : 'form-control'})
    confirm_password.widget.attrs.update({'placeholder' : '********'})

    def clean_confirm_password(self):
        PASSWORD_REGEX_PATTERN = "^([a-zA-Z0-9]+)+$"
        pattern = re.compile(PASSWORD_REGEX_PATTERN)
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]

        if not pattern.match(password):
            raise forms.ValidationError("A password can only contain letters from A-Z and digits.")

        if password != confirm_password:
            raise forms.ValidationError("The passwords do not match")

class SettingsForm(forms.Form):
    username = forms.CharField(max_length=100)
    username.widget.attrs.update({'class' : 'form-control'})

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document_name', 'description', 'document', 'project')

    def clean_document(self):
        content = self.cleaned_data['document']
        if content._size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content._size)))
        return content

class NewEventForm(forms.ModelForm):
    event_title = forms.CharField()
    event_title.widget.attrs.update({'class' : 'form-control'})

    start_date = forms.CharField()
    start_date.widget.attrs.update({'class' : 'form-control datepicker'})

    end_date = forms.CharField()
    end_date.widget.attrs.update({'class' : 'form-control datepicker'})

    type = forms.ChoiceField(choices = EVENT_TYPE_CHOICES, widget = forms.Select(), required = True, initial ='' )
    type.widget.attrs.update({'class' : 'form-control'})

    description = forms.CharField()
    description.widget.attrs.update({'class' : 'form-control'})

    class Meta:
        model = Event
        fields = ('event_title', 'type', 'start_date', 'end_date', 'added_by', 'description', 'project')
