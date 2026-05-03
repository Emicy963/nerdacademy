from django.urls import path
from .views import InstitutionDetailView, InstitutionRegisterView, InstitutionVerifyView

urlpatterns = [
    path("register/", InstitutionRegisterView.as_view(), name="institution-register"),
    path("verify/",   InstitutionVerifyView.as_view(),   name="institution-verify"),
    path("me/",       InstitutionDetailView.as_view(),   name="institution-me"),
]
