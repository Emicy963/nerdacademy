from django.urls import path
from .views import StudentListCreateView, StudentDetailView, MyStudentProfileView

urlpatterns = [
    path("", StudentListCreateView.as_view(), name="student-list-create"),
    path("me/", MyStudentProfileView.as_view(), name="student-me"),
    path("<uuid:student_id>/", StudentDetailView.as_view(), name="student-detail"),
]
