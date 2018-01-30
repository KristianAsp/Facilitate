from django.shortcuts import render
from django.template import loader
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.core import serializers as core_serializers
from .serializers import *
from django.http import HttpResponse, JsonResponse, QueryDict, Http404
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from .models import Project, Ticket, Profile
import json, pdb

class AuthenticateUser(APIView):
    def get(self, request):
        user = authenticate(request, username = request.POST.get("username"), password = request.POST.get("password"))
        if user is not None:
            return True
        return False

class LoginUser(APIView):
    def get(self, request):
        user = authenticate(request, username = request.POST.get("username"), password = request.POST.get("password"))
        if user is not None:
            login(request, user)
            return True
        return False

class LogoutUser(APIView):
    def get(self, request):
        logout(request)
        return True

class ProjectList(APIView):
    def get(self, request, format=None):
        auth_token = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
        token = Token.objects.get(key = auth_token)
        user = User.objects.get(username=token.user)
        profile = Profile.objects.get(user = user)

        projects = profile.projects.all()
        serializer = ProjectSerializer(projects, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, format=None):
        auth_token = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
        token = Token.objects.get(key = auth_token)
        user = User.objects.get(username = token.user)
        profile = Profile.objects.get(user = user)
        data = request.data.copy()
        data['owner'] = user.id
        serializer = ProjectSerializer(data = data)

        if serializer.is_valid():
            project = serializer.save()
            profile.projects.add(project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectDetail(APIView):
    def get_object(self, pk):
        try:
            return Project.objects.get(pk = pk)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        project = ProjectSerializer(project)
        return Response(project.data)

    def put(self, request, pk, format=None):
        project = self.get_object(pk)
        serializer = ProjectSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        project = self.get_object(pk)
        project.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class UserList(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk = pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        user = UserSerializer(user)
        return Response(user.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class TicketList(APIView):
    def get(self, request, pk, format=None):
        project = Project.objects.get(pk = pk)
        tickets = Ticket.objects.filter(project = project)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        serializer = TicketSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketDetail(APIView):
    def get_object(self, pk):
        try:
            return Ticket.objects.get(pk = pk)
        except Ticket.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        ticket = self.get_object(pk)
        ticket = TicketSerializer(user)
        return Response(ticket.data)

    def put(self, request, pk, format=None):
        ticket = self.get_object(pk)
        serializer = TicketSerializer(ticket, data = request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        ticket = self.get_object(pk)
        ticket.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


# @csrf_exempt
# def productIndex(request, id):
#     response_data = {}
#     if(request.method == "GET"):
#
#         response_data['hello'] = "This is a new get request. The ID is " + id
#         return JsonResponse(response_data)
#     if(request.method == "POST"):
#         response_data['intro'] = "I am creating a new post request"
#         nameIn = request.POST.get('name')
#         ownerIn = request.POST.get('owner')
#         project = Project(name = nameIn, owner = ownerIn)
#         project.save()
#
#     return JsonResponse(response_data)
#
# def users(request, id):
#     response_data = {}
#     if(request.method == "GET"):
#         response_data['hello'] = "This is a get request for to get a user"
#         return JsonResponse(response_data)
#     if(request.method == "POST"):
#         response_data['intro'] = "I am creating a new post request for a user"
#         nameIn = request.POST.get('username')
#         emailIn = request.POST.get('email')
#         passwordIn = request.POST.get('password')
#         user = User(name = nameIn, email = emailIn, password = passwordIn)
#         user.save()
#
#     return JsonResponse(response_data)
