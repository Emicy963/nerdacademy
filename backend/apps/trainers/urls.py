from django.urls import path
from .views import (
    TrainerListCreateView,
    TrainerDetailView,
    TrainerResetPasswordView,
    TrainerClassesView,
    MyTrainerProfileView,
)

urlpatterns = [
    path("", TrainerListCreateView.as_view(), name="trainer-list-create"),
    path("me/", MyTrainerProfileView.as_view(), name="trainer-me"),
    path("<uuid:trainer_id>/", TrainerDetailView.as_view(), name="trainer-detail"),
    path(
        "<uuid:trainer_id>/reset-password/",
        TrainerResetPasswordView.as_view(),
        name="trainer-reset-password",
    ),
    path(
        "<uuid:trainer_id>/classes/",
        TrainerClassesView.as_view(),
        name="trainer-classes",
    ),
]
