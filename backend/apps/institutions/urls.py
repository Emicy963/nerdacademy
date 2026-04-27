from django.urls import path
from .views import InstitutionDetailView, InstitutionRegisterView

urlpatterns = [
    path("register/", InstitutionRegisterView.as_view(), name="institution-register"),
    path("me/",       InstitutionDetailView.as_view(),   name="institution-me"),
]
