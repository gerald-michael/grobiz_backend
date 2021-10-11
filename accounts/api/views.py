from django.shortcuts import render
from rest_framework import generics
from accounts.api.serializers import *
from accounts.models import *
# Create your views here.


class UserDetails(generics.ListAPIView):
    serializer_class = SmeProfileSerializer
    queryset = SmeProfile.objects.all()
