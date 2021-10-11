from rest_framework import generics
from investment.api.serializers import *
from investment.models import *


class InvestmentList(generics.ListAPIView):
    serializer_class = InvestmentSerializer
    queryset = Investments.objects.all()


class InvestmentCreateView(generics.CreateAPIView):
    serializer_class = InvestmentSerializer
    queryset = Investments.objects.all()
