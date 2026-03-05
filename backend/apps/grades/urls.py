from django.urls import path
from .views import (
    GradeListCreateView,
    GradeDetailView,
    GradeReportView,
    MyGradesView,
    EnrollmentGradesView,
)

urlpatterns = [
    path("", GradeListCreateView.as_view(), name="grade-list-create"),
    path("report/", GradeReportView.as_view(), name="grade-report"),
    path("my-grades/", MyGradesView.as_view(), name="my-grades"),
    path("<uuid:grade_id>/", GradeDetailView.as_view(), name="grade-detail"),
    path(
        "enrollment/<uuid:enrollment_id>/",
        EnrollmentGradesView.as_view(),
        name="enrollment-grades",
    ),
]
