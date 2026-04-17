from django.urls import path
from .views import InstitutionDetailView

urlpatterns = [
    path("me/", InstitutionDetailView.as_view(), name="institution-me"),
]
