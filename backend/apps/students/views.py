from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import PaginatedListMixin
from core.permissions import IsAdminRole, IsTrainerRole
from .serializers import (
    StudentSerializer,
    StudentCreateSerializer,
    StudentUpdateSerializer,
    StudentPublicSerializer,
)
from .services import StudentService


class StudentListCreateView(PaginatedListMixin, APIView):
    """
    GET  /api/students/ — list students (admin + trainer)
    POST /api/students/ — create student (admin only)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated(), IsTrainerRole()]

    def get(self, request):
        search = request.query_params.get("search")
        is_active = request.query_params.get("is_active")

        if is_active is not None:
            is_active = is_active.lower() == "true"

        students = StudentService.list_students(
            institution=request.membership.institution,
            search=search,
            is_active=is_active,
        )
        return self.paginate(request, students, StudentSerializer)

    def post(self, request):
        serializer = StudentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student, temp_password = StudentService.create_student(
            institution=request.membership.institution,
            **serializer.validated_data,
        )
        response_data = StudentSerializer(student).data
        if temp_password:
            response_data["temp_password"] = temp_password
        return Response(response_data, status=status.HTTP_201_CREATED)


class StudentDetailView(APIView):
    """
    GET    /api/students/{id}/ — detail (admin + trainer)
    PATCH  /api/students/{id}/ — update (admin only)
    DELETE /api/students/{id}/ — deactivate (admin only)
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), IsTrainerRole()]
        return [IsAuthenticated(), IsAdminRole()]

    def _get_student(self, request, student_id):
        return StudentService.get_student(
            student_id=student_id,
            institution=request.membership.institution,
        )

    def get(self, request, student_id):
        student = self._get_student(request, student_id)
        return Response(StudentSerializer(student).data)

    def patch(self, request, student_id):
        student = self._get_student(request, student_id)
        serializer = StudentUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = StudentService.update_student(student, serializer.validated_data)
        return Response(StudentSerializer(updated).data)

    def delete(self, request, student_id):
        student = self._get_student(request, student_id)
        StudentService.deactivate_student(student)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyStudentProfileView(APIView):
    """
    GET /api/students/me/ — student views their own profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = StudentService.get_student_by_user(
            request.user, request.membership.institution
        )
        return Response(StudentPublicSerializer(student).data)
