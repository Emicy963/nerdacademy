from django.urls import path
from .views import (
    ClassListCreateView,
    ClassDetailView,
    ClassCloseView,
    EnrollmentListCreateView,
    EnrollmentDetailView,
    MyEnrollmentsView,
)

urlpatterns = [
    path("", ClassListCreateView.as_view(), name="class-list-create"),
    path("my-enrollments/", MyEnrollmentsView.as_view(), name="my-enrollments"),
    path("<uuid:class_id>/", ClassDetailView.as_view(), name="class-detail"),
    path("<uuid:class_id>/close/", ClassCloseView.as_view(), name="class-close"),
    path(
        "<uuid:class_id>/enrollments/",
        EnrollmentListCreateView.as_view(),
        name="enrollment-list-create",
    ),
    path(
        "<uuid:class_id>/enrollments/<uuid:enrollment_id>/",
        EnrollmentDetailView.as_view(),
        name="enrollment-detail",
    ),
]
