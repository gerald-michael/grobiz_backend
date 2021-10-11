from investment.models import *
from rest_framework import serializers


class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investments
        fields = "__all__"


class InvestmentCreate(serializers.ModelSerializer):
    class Meta:
        model = Investments
        fields = ["amount"]