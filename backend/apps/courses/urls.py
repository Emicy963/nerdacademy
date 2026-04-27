from django.urls import path
from .views import CourseListCreateView, CourseDetailView, CourseClassesView

urlpatterns = [
    path("", CourseListCreateView.as_view(), name="course-list-create"),
    path("<uuid:course_id>/", CourseDetailView.as_view(), name="course-detail"),
    path(
        "<uuid:course_id>/classes/", CourseClassesView.as_view(), name="course-classes"
    ),
]
