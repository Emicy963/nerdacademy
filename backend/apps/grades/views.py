from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import PaginatedListMixin
from core.permissions import IsAdminRole, IsTrainerRole
from .serializers import (
    GradeSerializer,
    GradeLaunchSerializer,
    GradeUpdateSerializer,
    GradeReportEntrySerializer,
    MyGradeSerializer,
)
from .services import GradeService


class GradeListCreateView(PaginatedListMixin, APIView):
    """
    GET  /api/grades/ — list grades (admin + trainer, filtered by params)
    POST /api/grades/ — launch a grade (trainer of the class + admin)
    """

    permission_classes = [IsAuthenticated, IsTrainerRole]

    def get(self, request):
        grades = GradeService.list_grades(
            institution=request.user.institution,
            enrollment_id=request.query_params.get("enrollment_id"),
            class_id=request.query_params.get("class_id"),
            student_id=request.query_params.get("student_id"),
            assessment_type=request.query_params.get("assessment_type"),
        )
        return self.paginate(request, grades, GradeSerializer)

    def post(self, request):
        serializer = GradeLaunchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        grade = GradeService.launch_grade(
            user=request.user,
            enrollment_id=str(data["enrollment_id"]),
            institution=request.user.institution,
            assessment_type=data["assessment_type"],
            value=data["value"],
            max_value=data["max_value"],
            assessed_at=data["assessed_at"],
            notes=data.get("notes", ""),
        )
        return Response(GradeSerializer(grade).data, status=status.HTTP_201_CREATED)


class GradeDetailView(APIView):
    """
    GET    /api/grades/{id}/ — grade detail
    PATCH  /api/grades/{id}/ — update grade (trainer of class + admin)
    DELETE /api/grades/{id}/ — delete grade (trainer of class + admin)
    """

    permission_classes = [IsAuthenticated, IsTrainerRole]

    def _get_grade(self, request, grade_id):
        return GradeService.get_grade(
            grade_id=grade_id,
            institution=request.user.institution,
        )

    def get(self, request, grade_id):
        grade = self._get_grade(request, grade_id)
        return Response(GradeSerializer(grade).data)

    def patch(self, request, grade_id):
        grade = self._get_grade(request, grade_id)
        serializer = GradeUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = GradeService.update_grade(
            user=request.user,
            grade=grade,
            data=serializer.validated_data,
        )
        return Response(GradeSerializer(updated).data)

    def delete(self, request, grade_id):
        grade = self._get_grade(request, grade_id)
        GradeService.delete_grade(user=request.user, grade=grade)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GradeReportView(APIView):
    """
    GET /api/grades/report/?class_id={id}
    Full grade report for a class: all students, all grades, averages.
    Admin + trainer of that class.
    """

    permission_classes = [IsAuthenticated, IsTrainerRole]

    def get(self, request):
        class_id = request.query_params.get("class_id")
        if not class_id:
            return Response(
                {"detail": 'query param "class_id" is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Trainers can only report on their own classes
        if request.user.is_trainer:
            from apps.classes.services import ClassService
            from apps.trainers.services import TrainerService

            try:
                trainer = TrainerService.get_trainer_by_user(request.user)
                class_instance = ClassService.get_class(
                    class_id, request.user.institution
                )
                if str(class_instance.trainer_id) != str(trainer.id):
                    return Response(
                        {"detail": "You can only view reports for your own classes."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        report = GradeService.get_class_report(class_id, request.user.institution)
        serializer = GradeReportEntrySerializer(report, many=True)
        return Response(serializer.data)


class MyGradesView(APIView):
    """
    GET /api/grades/my-grades/ — student views all their own grades.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.students.services import StudentService

        student = StudentService.get_student_by_user(request.user)
        grades = GradeService.get_grades_for_student(student)

        # Group by class for a richer response
        grouped = {}
        for grade in grades:
            class_id = str(grade.enrollment.class_instance_id)
            class_name = grade.enrollment.class_instance.name
            course_name = grade.enrollment.class_instance.course.name
            trainer_name = grade.enrollment.class_instance.trainer.full_name

            if class_id not in grouped:
                grouped[class_id] = {
                    "class_id": class_id,
                    "class_name": class_name,
                    "course_name": course_name,
                    "trainer_name": trainer_name,
                    "grades": [],
                    "average": None,
                }
            grouped[class_id]["grades"].append(MyGradeSerializer(grade).data)

        # Compute average per class
        from apps.classes.models import Enrollment

        for class_id, entry in grouped.items():
            enrollment = Enrollment.objects.filter(
                student=student,
                class_instance_id=class_id,
            ).first()
            if enrollment:
                entry["average"] = str(GradeService.calculate_average(enrollment))

        return Response(list(grouped.values()))


class EnrollmentGradesView(PaginatedListMixin, APIView):
    """
    GET /api/grades/enrollment/{enrollment_id}/
    All grades for a specific enrollment.
    Trainer (own class) + Admin.
    """

    permission_classes = [IsAuthenticated, IsTrainerRole]

    def get(self, request, enrollment_id):
        grades = GradeService.list_grades(
            institution=request.user.institution,
            enrollment_id=str(enrollment_id),
        )
        return self.paginate(request, grades, GradeSerializer)
