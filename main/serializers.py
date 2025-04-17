from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User,
        fields = ['id', 'username', 'email']

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session,
        fields = ['name']
    
class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise,
        fields = ['name', 'reps', 'makes', 'accuracy', 'checked']

class TasksSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tasks,
        fields = ['name', 'checked']