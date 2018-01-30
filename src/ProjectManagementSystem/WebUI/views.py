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
from .forms import *
from WebAPI.models import Profile
import pdb
from django_tables2 import RequestConfig
from .tables import TicketTable
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
    try:
        if request.session['active_project']:
            return HttpResponseRedirect("/dashboard/" + request.session['active_project'])
    except:
        print("No active project")
    # SAMPLE GET REQUEST
    ######
    data = {'projects' : getProjects(request), }
    template = loader.get_template('UI/user/dashboard.html')
    return HttpResponse(template.render(data, request))

@login_required
def profile_index(request):
    form = ProfileForm()
    return render(request, 'UI/user/profile.html', {'form': form})

def getProjects(request):
    rootURL = API_URL + 'projects/'

    data = {'content-type': 'application/json', 'Authorization' : 'Token ' + request.session['auth']}
    try:
        ro = requests.get(rootURL, headers = data)
        return ro.json()
    except ValueError:
        return {}

def getSingleProject(request, pk):
    rootURL = API_URL + 'projects/' + pk + '/'
    data = {'content-type': 'application/json', 'Authorization' : 'Token ' + request.session['auth']}

    try:
        ro = requests.get(rootURL, headers = data)
        return ro.json()
    except ValueError:
        return {}


@login_required
def settings_index(request):
    form = SettingsForm()
    return render(request, 'UI/user/settings.html', {'form': form})


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
        if request.user.is_authenticated:
            return HttpResponseRedirect("/dashboard")
        form = RegisterForm()
        return render(request, 'UI/register.html', {'form': form})

    return HttpResponseBadRequest

def login_index(request):
    if request.method == "POST":
        return user_login(request)

    if request.method == "GET":
        if request.user.is_authenticated:
            return HttpResponseRedirect("/dashboard")
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
def dashboard_project_view(request, pk):
    rootURL = API_URL + 'projects/tickets/' + pk
    request.session['active_project'] = pk
    project = getSingleProject(request, pk);
    request.session['is_owner'] = project['owner'] == request.user.id

    data = {
            'projects' : getProjects(request),
            'tickets' : getTickets(request),
            }
    template = loader.get_template('UI/user/dashboard.html')
    return HttpResponse(template.render(data, request))

def getTickets(request):
    rootURL = API_URL + 'projects/' + request.session['active_project'] + "/tickets"

    data = {'content-type': 'application/json', 'Authorization' : 'Token ' + request.session['auth']}
    try:
        ro = requests.get(rootURL, headers = data)
        return ro.json()
    except ValueError:
        return {}

@login_required
def dashboard_ticket_view(request):
    tickets = getTickets(request)

    table = TicketTable(tickets)
    RequestConfig(request).configure(table)
    data = {
        'projects' : getProjects(request),
        'tickets' : getTickets(request),
        'table' : table,
        }
    return render(request, 'UI/project/tasklist.html', data)

@login_required
def new_ticket_view(request):
    if request.method == "GET":
        form = NewTicketForm()
        return render(request, 'UI/project/tickets/new.html', {'form': form})
    elif request.method == "POST":
        form = NewTicketForm(request.POST)
        if form.is_valid():
            data = { 'Authorization' : 'Token ' + request.session['auth']}
            rootURL = API_URL + 'projects/' + request.session['active_project'] + "/tickets/"
            post_fields = form.cleaned_data
            post_fields['project'] = request.session['active_project']
            response = requests.post(rootURL, headers = data, data = post_fields)
            responseJsonParsed = json.dumps(response.text)
            return render(request, 'UI/project/tickets/new.html', {'form' : form, 'message' : 'The project was successfully created' })
