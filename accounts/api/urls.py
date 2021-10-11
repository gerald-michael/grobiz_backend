from django.urls import path, include
from accounts.api.views import *
urlpatterns = [
    path('auth/', include('rest_auth.urls')),
    path('auth/sme_profile', UserDetails.as_view()),
    path('auth/register/', include('rest_auth.registration.urls')),
]
