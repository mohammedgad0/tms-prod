from django.contrib.auth.models import User, Group
from .models import Employee, Sheet
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sheet
        fields = ('taskdesc', 'taskdate')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
