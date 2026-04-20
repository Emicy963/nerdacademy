from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import PaginatedListMixin
from core.permissions import IsAdminRole, IsTrainerRole
from .serializers import (
    CourseSerializer,
    CourseCreateSerializer,
    CourseUpdateSerializer,
)
from .services import CourseService


class CourseListCreateView(PaginatedListMixin, APIView):
    """
    GET  /api/courses/ — list courses (admin + trainer + student)
    POST /api/courses/ — create course (admin only)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]

    def get(self, request):
        search = request.query_params.get("search")
        is_active = request.query_params.get("is_active")

        if is_active is not None:
            is_active = is_active.lower() == "true"
        else:
            # Default: only show active courses to non-admins
            if not request.membership.is_admin:
                is_active = True

        courses = CourseService.list_courses(
            institution=request.membership.institution,
            search=search,
            is_active=is_active,
        )
        return self.paginate(request, courses, CourseSerializer)

    def post(self, request):
        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = CourseService.create_course(
            institution=request.membership.institution,
            **serializer.validated_data,
        )
        return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)


class CourseDetailView(APIView):
    """
    GET    /api/courses/{id}/ — detail (all authenticated)
    PUT    /api/courses/{id}/ — full update (admin only)
    PATCH  /api/courses/{id}/ — partial update (admin only)
    DELETE /api/courses/{id}/ — deactivate (admin only)
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminRole()]

    def _get_course(self, request, course_id):
        return CourseService.get_course(
            course_id=course_id,
            institution=request.membership.institution,
        )

    def get(self, request, course_id):
        course = self._get_course(request, course_id)
        return Response(CourseSerializer(course).data)

    def put(self, request, course_id):
        course = self._get_course(request, course_id)
        serializer = CourseUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = CourseService.update_course(course, serializer.validated_data)
        return Response(CourseSerializer(updated).data)

    def patch(self, request, course_id):
        course = self._get_course(request, course_id)
        serializer = CourseUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = CourseService.update_course(course, serializer.validated_data)
        return Response(CourseSerializer(updated).data)

    def delete(self, request, course_id):
        course = self._get_course(request, course_id)
        CourseService.deactivate_course(course)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseClassesView(PaginatedListMixin, APIView):
    """
    GET /api/courses/{id}/classes/ — list all classes for a course.
    Available to admin and trainers.
    """

    permission_classes = [IsAuthenticated, IsTrainerRole]

    def get(self, request, course_id):
        course = CourseService.get_course(
            course_id=course_id,
            institution=request.membership.institution,
        )
        classes = CourseService.get_course_classes(course)

        from apps.classes.serializers import ClassSummarySerializer

        return self.paginate(request, classes, ClassSummarySerializer)
