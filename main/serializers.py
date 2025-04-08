from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User,
        fields = ['username', 'email', 'password'],
        extra_kwargs = {'password':{'write_only':True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email', ''],
            password=validated_data['password'],
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
        fields = ['name', 'reps', 'makes', 'accuracy']