from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, JsonResponse, QueryDict, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string, get_template
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from django.core.mail import EmailMessage
import requests, json
import hashlib
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django_tables2 import RequestConfig
from .tables import TicketTable
from .forms import *
from WebAPI.models import Profile
from WebAPI.models import Invitation, Project, Profile
import pdb, re, uuid

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
    data = {'projects' : getProjects(request), }
    try:
        if request.session['active_project']:
            return HttpResponseRedirect("/dashboard/" + request.session['active_project'])
    except:
        try:
            request.session['active_project'] = str(data['projects'][0]['id'])
            return HttpResponseRedirect("/dashboard/" + request.session['active_project'])
        except:
            template = loader.get_template('UI/user/dashboard.html')
            return HttpResponse(template.render(data, request))

    template = loader.get_template('UI/user/dashboard.html')
    return HttpResponse(template.render(data, request))

@login_required
def profile_index(request):
    form = ProfileForm()
    return render(request, 'UI/user/profile.html', {'form': form, 'user': request.user})

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
        invitations = Invitation.objects.filter(user = user.email)

        profile.save()
        for invitation in invitations:
            profile.projects.add(invitation.project)

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
            if(request.POST['public']):
                post_fields['visibility'] = True
            response = requests.post(rootURL, headers = data, data = post_fields)
            responseJsonParsed = json.dumps(response.text)
            return render(request, 'UI/project/new.html', {'form' : form, 'message' : 'The project was successfully created' })

@csrf_exempt
def delete_project(request):
    if request.method == "POST":
        data = { 'Authorization' : 'Token ' + request.session['auth']}
        project = request.session['active_project']
        del request.session['active_project']
        rootURL = 'http://127.0.0.1:8000/api/projects/' + project
        response = requests.delete(rootURL, headers = data)
        responseJsonParsed = json.dumps(response.text)
        form = NewProjectForm()
        return render(request, 'UI/project/new.html', {'form' : form, 'message' : 'The project was successfully deleted' })

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

def getUsersForProject(request, project_id):
    rootURL = API_URL + 'projects/' + project_id + '/users/all'
    data = { 'Authorization' : 'Token ' + request.session['auth']}
    response = requests.get(rootURL, headers = data)
    responseJsonParsed = json.loads(response.text)
    return responseJsonParsed

@login_required
def project_settings_view(request):
    if request.method == "GET":
        data = getUsersForProject(request, request.session['active_project'])
        context = {}
        context['data'] = data
        if 'error_message' in request.session:
            context['error_message'] = request.session['error_message']
            del request.session['error_message']
        elif 'message' in request.session:
            context['message'] = request.session['message']
            del request.session['message']
        return render(request, 'UI/project/settings.html', context)
    elif request.method == "POST":
        return user_project_settings(request)

@login_required
def user_project_settings(request):
    if request.method == "POST":
        error_message = None
        try:
            rootURL = API_URL + 'profiles/' + request.POST['txtUser'] + '/'
            data = { 'Authorization' : 'Token ' + request.session['auth']}
            response = requests.get(rootURL, headers = data)
            if response.status_code == 500:
                raise User.DoesNotExist #Raise exception for User that do not exist
            elif response.status_code == 401:
                raise PermissionDenied
            responseJsonParsed = json.loads(response.text)
            projects = responseJsonParsed['projects']

            if int(request.session['active_project']) not in projects:
                projects.append(int(request.session['active_project']))
                responseJsonParsed['projects'] = projects
                response = requests.put(rootURL, headers = data, data = responseJsonParsed)
                request.session['message'] =  request.POST['txtUser'] + ' was successfully added to the project.'
            else:
                error_message = "This user is already a collaborator on this project!"
                request.session['error_message'] = error_message
        except (User.DoesNotExist, Profile.DoesNotExist):
            print ("Need to send an email now")
            error_message = "No user with that name."
            request.session['error_message'] = error_message
            EMAIL_REGEX = "[^@]+@[^@]+\.[^@]+" # Move this to a file to contain all REGEXs
            if re.match(EMAIL_REGEX, request.POST['txtUser']): ##If the non-existant user is an email address, send an invitation by email to use the software.

                createInvitation(request.user, request.POST['txtUser'], request.session['active_project'])
                message = "An invitation has been sent to this email address."
                request.session['message'] = message
                del request.session['error_message']
        except PermissionDenied:
            error_message = "You are not allowed to do that."
            request.session['error_message'] = error_message
        return HttpResponseRedirect('/project/settings')
    elif request.method == "GET":
        data = getUsersForProject(request, request.session['active_project'])
        data_arr = []
        for user in data:
            data_arr.append(user['username'])
        return JsonResponse(data_arr, safe=False)


def createInvitation(user, email, project):
    try:
        invitation = Invitation.objects.get(project = project, user = email)
        print("An invitation for this user already exist")
    except Invitation.DoesNotExist:
        project = Project.objects.get(id = project)
        invitation = Invitation(project = project, user = email, invitor = user)
        invitation.save()
        print("Created an invitation")

def view_user_profile(request, slug):
    responseJsonParsed = None
    form = ProfileForm()
    rootURL = API_URL + 'users/' + slug + '/'
    data = { 'Authorization' : 'Token ' + request.session['auth']}
    response = requests.get(rootURL, headers = data)
    if response.status_code == 500:
        raise User.DoesNotExist #Raise exception for User that do not exist
    elif response.status_code == 404:
        raise Http404
    else:
        responseJsonParsed = json.loads(response.text)
        del responseJsonParsed['password']

    return render(request, 'UI/user/profile.html', {'form': form, 'user': responseJsonParsed })

def search(request):
    context = {
            'users' : filterUsers(request, request.GET['query']),
            'projects' : filterProjects(request, request.GET['query']),
            }
    return render(request, 'UI/search/search.html')

def filterUsers(request, query):
    list_of_query_words = query.split(" ")
    filteredUsers = []
    for word in list_of_query_words:
        filteredUsers += User.objects.filter(username__icontains = word)
    return filteredUsers;

def filterProjects(request, query):
    list_of_query_words = query.split(" ")
    filteredProjects = []
    for word in list_of_query_words:
        filteredProjects += Project.objects.filter(name__icontains = word, visibility = True)
    return filteredProjects;

def handler404(request):
    response = render(request, 'UI/login.html', status=404)
    return response

def remove_user_from_project(request, slug):
    user = User.objects.get(username = slug)
    profile = Profile.objects.get(user = user)
    project = Project.objects.get(id = request.session['active_project'])
    profile.projects.remove(project)
    request.session['message'] =  user.username + ' was successfully removed from the project.'
    return HttpResponseRedirect('/project/settings')

def forgotten_password(request):
    if request.method == "GET":
        return render(request, 'UI/forgotten_password.html')
    elif request.method == "POST":
        email = request.POST['email']
        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            return render(request, 'UI/forgotten_password.html', {'error' : 'We could not find a user with that email address. Please try again'})

        user.set_unusable_password()
        user.save()
        profile = Profile.objects.get(user = user)
        profile.reset_password_hash = uuid.uuid1().hex
        profile.save()
        send_email('UI/email/reset_password.html', ['kristian.aspevik@gmail.com'], 'Reset Password', slug = profile.reset_password_hash, )
        return render(request, 'UI/forgotten_password.html', {'message' : 'An email has been sent to ' + email})

def reset_password(request, slug):
    if request.method == "GET":
        try:
            profile = Profile.objects.get(reset_password_hash = slug)
            user = User.objects.get(profile = profile)
        except (Profile.DoesNotExist, User.DoesNotExist):
            raise Http404
        return render(request, 'UI/reset_password.html', {'slug' : slug})
    elif request.method == "POST":
        try:
            profile = Profile.objects.get(reset_password_hash = slug)
            user = User.objects.get(profile = profile)
        except (Profile.DoesNotExist, User.DoesNotExist):
            raise Http404

        new_pass = request.POST.get('password')
        user.set_password(new_pass)
        user.save()
        profile.reset_password_hash = None
        profile.save()
        return render(request, 'UI/reset_password.html', {'message' : 'Success', 'slug' : slug})

def send_email(template, recipients, subject, **kwargs):
    message = get_template(template).render(kwargs)
    email = EmailMessage(subject, message, to=recipients)
    email.content_subtype = 'html'
    email.send()
