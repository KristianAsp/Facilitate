from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK
from rest_framework.authtoken.models import Token
from .serializers import ProjectSerializer, UserSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
