from django.urls import path, include
from .views import *
urlpatterns = [
    path("", InvestmentList.as_view()),
    path("create/", InvestmentCreateView.as_view()),
]
