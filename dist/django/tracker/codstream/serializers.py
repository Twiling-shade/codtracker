from rest_framework import serializers
from .models import *

class usersSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = "__all__"

class mpSerializer(serializers.ModelSerializer):
    class Meta:
        model = mp
        fields = "__all__"

class wzSerializer(serializers.ModelSerializer):
    class Meta:
        model = wz
        fields = "__all__"

class cwSerializer(serializers.ModelSerializer):
    class Meta:
        model = cw
        fields = "__all__"

class databaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = database
        fields = "__all__"
