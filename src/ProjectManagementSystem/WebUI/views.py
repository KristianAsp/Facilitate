from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, JsonResponse, QueryDict, HttpResponseRedirect, HttpResponseBadRequest
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import requests, json
import hashlib
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm, NewProjectForm
from WebAPI.models import Profile
import pdb

API_URL = 'http://127.0.0.1:8000/api/'

######
# Obtain authentication token from API
######
def get_auth_token(request, username, password):
    URL = API_URL + 'get_auth_token/'
    data = dict(username = username, password = password)

    r = requests.post(URL, data = data)
    data_json = r.json()
    request.session['auth'] = data_json['token']

@csrf_exempt
def user_login(request):
    form = LoginForm(request.POST)

    if form.is_valid():
        username = request.POST.get("username") #cleaned_data.get did not work. Find out why
        password = request.POST.get("password") #cleaned_data.get did not work. Find out why

        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            get_auth_token(request, username = username, password = password)
            return HttpResponseRedirect('/dashboard/')
    return render(request, 'UI/login.html', {'form': form})

@login_required
def dashboard_index(request):
    rootURL = API_URL + 'projects/'

    # SAMPLE GET REQUEST
    ######
    data = {'content-type': 'application/json', 'Authorization' : 'Token ' + request.session['auth']}
    try:
        ro = requests.get(rootURL, headers = data)
        data = {'projects' : ro.json(), }
    except ValueError:
        data = {}
        print('error')
    template = loader.get_template('UI/user/dashboard.html')
    return HttpResponse(template.render(data, request))

def user_register(request):
    form = RegisterForm(request.POST)

    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get('password'))
        user.save()
        profile = Profile(user = user)
        profile.save()
        login(request, user)
        get_auth_token(request, username = user.username, password = form.cleaned_data.get('password'))
        return HttpResponseRedirect('/dashboard/')
    return render(request, 'UI/register.html', {'form': form})

def register_index(request):
    if request.method == "POST":
        return user_register(request)

    if request.method == "GET":
        form = RegisterForm()
        return render(request, 'UI/register.html', {'form': form})

    return HttpResponseBadRequest

def login_index(request):
    if request.method == "POST":
        return user_login(request)

    if request.method == "GET":
        form = LoginForm()
        return render(request, 'UI/login.html', {'form': form})

    return HttpResponseBadRequest

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def index(request):
    context = {}
    template = loader.get_template('UI/index.html')
    return HttpResponse(template.render(context, request))

@login_required
def new_project(request):
    if request.method == "GET":
        form = NewProjectForm()
        return render(request, 'UI/project/new.html', {'form' : form})

    if request.method == "POST":
        form = NewProjectForm(request.POST)

        if form.is_valid():
            data = { 'Authorization' : 'Token ' + request.session['auth']}
            rootURL = 'http://127.0.0.1:8000/api/projects/'
            post_fields = form.cleaned_data
            response = requests.post(rootURL, headers = data, data = post_fields)
            responseJsonParsed = json.dumps(response.text)
            return render(request, 'UI/project/new.html', {'form' : form, 'message' : 'The project was successfully created' })

@login_required
def display_tickets(request, id):
    rootURL = API_URL + 'projects/tickets/' + id

    data = {'content-type': 'application/json', 'Authorization' : 'Token ' + request.session['auth']}
    try:
        ro = requests.get(rootURL, headers = data)
        data = {'tickets' : ro.json(), }
    except ValueError:
        data = {}
        print('error')
    template = loader.get_template('UI/user/dashboard.html')
    return HttpResponse(template.render(data, request))
