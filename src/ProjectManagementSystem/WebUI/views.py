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


def user_login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username = username, password = password)
    if user is not None:
        login(request, user)
    else:
        return HttpResponseRedirect('/')
    return HttpResponseRedirect('/dashboard/')

@login_required
def dashboard_index(request):
    context = {}
    template = loader.get_template('UI/user/dashboard.html')
    return HttpResponse(template.render(context, request))

def user_register(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    email = request.POST.get("email")

    new_user = User(username = username, email = email)
    new_user.set_password(password)
    new_user.save()
    user = authenticate(request, username = username, password = password)
    if not user:
        return HttpResponseRedirect('https://www.google.com')
    if user.is_authenticated:
        login(request, user)
    return HttpResponseRedirect('/dashboard/')

def register_index(request):
    context = {}
    template = loader.get_template('UI/register.html')
    return HttpResponse(template.render(context, request))

def login_index(request):
    if request.method == "POST":
        return user_login(request)

    if request.method == "GET":
        context = {}
        template = loader.get_template('UI/login.html')
        return HttpResponse(template.render(context, request))

    return HttpResponseBadRequest

@login_required
def user_logout(request):
    logout(user)
    return HttpResponseRedirect('/')

def index(request):
    context = {}
    template = loader.get_template('UI/index.html')
    return HttpResponse(template.render(context, request))
    #rootURL = 'http://127.0.0.1:8000/products/1/'

    #######
    # SAMPLE GET REQUEST
    ######
    #r = urlopen(rootURL).read().decode('utf-8')
    #data = json.loads(r)
    #html = "<html><body><pre>Data: %s.</pre></body></html>" % json.dumps(data['hello'], indent=2)

    #######
    # SAMPLE POST REQUEST
    ######
    #post_fields = {'name': 'My Project Name', 'owner':'Kristian'}
    #response = requests.post(rootURL, data = post_fields)
    #responseJsonParsed = json.loads(response.text)
    #return JsonResponse(responseJsonParsed)
