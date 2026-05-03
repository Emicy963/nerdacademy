from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import PaginatedListMixin
from core.permissions import IsAdminRole, IsTrainerRole
from apps.courses.models import Course
from apps.trainers.models import Trainer
from apps.students.models import Student
from .serializers import (
    ClassSerializer,
    ClassCreateSerializer,
    ClassUpdateSerializer,
    ClassDetailSerializer,
    EnrollmentSerializer,
    EnrollmentCreateSerializer,
    EnrollmentDetailSerializer,
)
from .services import ClassService, EnrollmentService


class ClassListCreateView(PaginatedListMixin, APIView):
    """
    GET  /api/classes/ — list classes (filtered by membership role)
    POST /api/classes/ — create class (admin only)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]

    def get(self, request):
        membership = request.membership
        institution = membership.institution

        # Students only see classes they are enrolled in
        if membership.is_student:
            try:
                from apps.students.services import StudentService

                student = StudentService.get_student_by_user(request.user, institution)
                classes = ClassService.list_classes_for_student(student)
            except Exception:
                classes = []
            return self.paginate(request, classes, ClassSerializer)

        # Trainers only see their own classes
        if membership.is_trainer:
            try:
                from apps.trainers.services import TrainerService

                trainer = TrainerService.get_trainer_by_user(request.user, institution)
                classes = ClassService.list_classes_for_trainer(trainer)
            except Exception:
                classes = []
            return self.paginate(request, classes, ClassSerializer)

        # Admins see all with optional filters
        classes = ClassService.list_classes(
            institution=institution,
            status=request.query_params.get("status"),
            course_id=request.query_params.get("course_id"),
            trainer_id=request.query_params.get("trainer_id"),
            search=request.query_params.get("search"),
        )
        return self.paginate(request, classes, ClassSerializer)

    def post(self, request):
        serializer = ClassCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        institution = request.membership.institution

        try:
            course = Course.objects.get(id=data["course_id"], institution=institution)
        except Course.DoesNotExist:
            return Response(
                {"course_id": "Course not found."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            trainer = Trainer.objects.get(
                id=data["trainer_id"], institution=institution
            )
        except Trainer.DoesNotExist:
            return Response(
                {"trainer_id": "Trainer not found."}, status=status.HTTP_400_BAD_REQUEST
            )

        class_instance = ClassService.create_class(
            institution=institution,
            course=course,
            trainer=trainer,
            name=data["name"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
        return Response(
            ClassSerializer(class_instance).data, status=status.HTTP_201_CREATED
        )


class ClassDetailView(APIView):
    """
    GET    /api/classes/{id}/ — detail (admin + trainer)
    PATCH  /api/classes/{id}/ — update (admin only)
    DELETE /api/classes/{id}/ — delete if empty (admin only)
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), IsTrainerRole()]
        return [IsAuthenticated(), IsAdminRole()]

    def _get_class(self, request, class_id):
        return ClassService.get_class(
            class_id=class_id,
            institution=request.membership.institution,
        )

    def get(self, request, class_id):
        class_instance = self._get_class(request, class_id)

        if request.membership.is_trainer:
            try:
                from apps.trainers.services import TrainerService

                trainer = TrainerService.get_trainer_by_user(
                    request.user, request.membership.institution
                )
                if str(class_instance.trainer_id) != str(trainer.id):
                    return Response(
                        {"detail": "You can only view your own classes."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Exception:
                return Response(
                    {"detail": "Trainer profile not found."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(ClassDetailSerializer(class_instance).data)

    def patch(self, request, class_id):
        class_instance = self._get_class(request, class_id)
        serializer = ClassUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if "trainer_id" in data:
            try:
                data["trainer"] = Trainer.objects.get(
                    id=data.pop("trainer_id"),
                    institution=request.membership.institution,
                )
            except Trainer.DoesNotExist:
                return Response(
                    {"trainer_id": "Trainer not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        updated = ClassService.update_class(class_instance, data)
        return Response(ClassSerializer(updated).data)

    def delete(self, request, class_id):
        class_instance = self._get_class(request, class_id)
        ClassService.delete_class(class_instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClassCloseView(APIView):
    """POST /api/classes/{id}/close/ — Admin only."""

    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, class_id):
        class_instance = ClassService.get_class(
            class_id=class_id,
            institution=request.membership.institution,
        )
        closed = ClassService.close_class(class_instance)
        return Response(ClassSerializer(closed).data)


class EnrollmentListCreateView(PaginatedListMixin, APIView):
    """
    GET  /api/classes/{id}/enrollments/ — list (admin + trainer)
    POST /api/classes/{id}/enrollments/ — enroll (admin only)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated(), IsTrainerRole()]

    def _get_class(self, request, class_id):
        return ClassService.get_class(
            class_id=class_id,
            institution=request.membership.institution,
        )

    def get(self, request, class_id):
        class_instance = self._get_class(request, class_id)

        if request.membership.is_trainer:
            try:
                from apps.trainers.services import TrainerService

                trainer = TrainerService.get_trainer_by_user(
                    request.user, request.membership.institution
                )
                if str(class_instance.trainer_id) != str(trainer.id):
                    return Response(
                        {
                            "detail": "You can only view enrollments for your own classes."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Exception:
                return Response(
                    {"detail": "Trainer profile not found."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        enroll_status = request.query_params.get("status")
        enrollments = EnrollmentService.list_enrollments(
            class_instance, status=enroll_status
        )
        return self.paginate(request, enrollments, EnrollmentSerializer)

    def post(self, request, class_id):
        class_instance = self._get_class(request, class_id)
        serializer = EnrollmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            student = Student.objects.get(
                id=serializer.validated_data["student_id"],
                institution=request.membership.institution,
            )
        except Student.DoesNotExist:
            return Response(
                {"student_id": "Student not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        enrollment = EnrollmentService.enroll_student(class_instance, student)
        return Response(
            EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED
        )


class EnrollmentDetailView(APIView):
    """
    GET    /api/classes/{class_id}/enrollments/{id}/ — detail
    DELETE /api/classes/{class_id}/enrollments/{id}/ — drop (admin only)
    """

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated(), IsTrainerRole()]

    def _get_enrollment(self, request, class_id, enrollment_id):
        from rest_framework.exceptions import NotFound as DRFNotFound
        enrollment = EnrollmentService.get_enrollment(
            enrollment_id=enrollment_id,
            institution=request.membership.institution,
        )
        if str(enrollment.class_instance_id) != str(class_id):
            raise DRFNotFound()
        return enrollment

    def get(self, request, class_id, enrollment_id):
        enrollment = self._get_enrollment(request, class_id, enrollment_id)
        return Response(EnrollmentDetailSerializer(enrollment).data)

    def delete(self, request, class_id, enrollment_id):
        enrollment = self._get_enrollment(request, class_id, enrollment_id)
        EnrollmentService.drop_enrollment(enrollment)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyEnrollmentsView(PaginatedListMixin, APIView):
    """GET /api/classes/my-enrollments/ — student sees their own enrollments."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.students.services import StudentService

        student = StudentService.get_student_by_user(
            request.user, request.membership.institution
        )
        enroll_status = request.query_params.get("status")
        enrollments = EnrollmentService.list_enrollments_for_student(
            student=student,
            status=enroll_status,
        )
        return self.paginate(request, enrollments, EnrollmentDetailSerializer)
