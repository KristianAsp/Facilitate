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
from django.core.exceptions import PermissionDenied
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
        auth_token = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
        token = Token.objects.get(key = auth_token)
        user = User.objects.get(username = token.user)
        project = self.get_object(pk)

        if not project.owner == user:
            return PermissionDenied

        project.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class ProjectUsersList(APIView):
    def get(self, request, project, format=None):
        profile = Profile.objects.get(user = user)
        projects = profile.projects.all()
        serializer = ProjectSerializer(projects, many=True)
        return JsonResponse(serializer.data, safe=False)

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

    def put(self, request, pk, format=None):
        auth_token = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
        token = Token.objects.get(key = auth_token)
        user = User.objects.get(username = token.user)

        serializer = UserSerializer(user, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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

class UserDetailEmail(APIView):
    def get_object(self, email):
        try:
            return User.objects.get(email = email)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, email, format=None):
        user = self.get_object(email)
        user = UserSerializer(user)
        return Response(user.data)

    def put(self, request, email, format=None):
        user = self.get_object(email)
        serializer = UserSerializer(user, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, email, format=None):
        user = self.get_object(email)
        user.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class UserDetailUsername(APIView):
    def get_object(self, slug):
        try:
            return User.objects.get(username = slug)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        user = self.get_object(slug)
        user = UserSerializer(user)
        return Response(user.data)

    def put(self, request, slug, format=None):
        user = self.get_object(slug)
        serializer = UserSerializer(user, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, format=None):
        user = self.get_object(slug)
        user.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class ProfileList(APIView):
    def get(self, request, format=None):
        profile = Profile.objects.all()
        serializer = ProfileSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProfileSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileDetail(APIView):
    def get_object(self, pk):
        try:
            return Profile.objects.get(user = User.objects.get(pk = pk))
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        profile = self.get_object(pk)
        profile = ProfileSerializer(profile)
        return Response(profile.data)

    def put(self, request, pk, format=None):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(profile, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        profile = self.get_object(pk)
        profile.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class ProfileDetailEmail(APIView):
    def get_object(self, email):
        try:
            user = User.objects.get(email = email)
            return Profile.objects.get(user = user)
        except Profile.DoesNotExist:
            raise Http404

    def get(self, request, email, format=None):
        profile = self.get_object(email)
        profile = ProfileSerializer(profile)
        return Response(profile.data)

    def put(self, request, email, format=None):
        profile = self.get_object(email)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, email, format=None):
        profile = self.get_object(email)
        profile.delete()
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

class ProjectUsers(APIView):
    def get_objects(self, pk):
        try:
            profiles = Profile.objects.filter(projects__in=[pk])
            users = User.objects.filter(profile__in=profiles)
            return users
        except User.DoesNotExist:
            return Http404

    def get(self, request, pk, format=None):
        users = self.get_objects(pk)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class InvitationList(APIView):
    def get(self, request, format=None):
        invitations = invitation.objects.all()
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = InvitationSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvitationDetail(APIView):
    def get_object(self, pk):
        try:
            return Invitation.objects.get(pk = pk)
        except invitation.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        invitation = self.get_object(pk)
        invitation = InvitationSerializer(invitation)
        return Response(invitation.data)

    def put(self, request, pk, format=None):
        invitation = self.get_object(pk)
        serializer = InvitationSerializer(invitation, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        invitation = self.get_object(pk)
        invitation.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)
