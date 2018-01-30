from rest_framework import serializers
from .models import Project, Ticket
from django.contrib.auth.models import User
import pdb


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'owner')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('id', 'name', 'description', 'project', 'type', 'priority', 'state')

    def update(self, instance, validated_data):
        instance.state = validated_data.get('state', instance.state)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.project = validated_data.get('project', instance.project)
        instance.type = validated_data.get('type', instance.type)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.save()
        return instance
