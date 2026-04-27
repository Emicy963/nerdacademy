from decimal import Decimal, ROUND_HALF_UP
from django.db import IntegrityError
from django.db.models import Avg, Count, Q
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from apps.classes.models import Enrollment
from .models import Grade


class GradeService:

    @staticmethod
    def _validate_trainer_owns_class(user, membership, enrollment: Enrollment) -> None:
        """
        Ensures the requesting trainer is the assigned trainer
        for the class this enrollment belongs to.
        Admins bypass this check.
        membership is a Membership instance from request.membership.
        """
        if membership is None:
            raise PermissionDenied("No active membership context.")
        if membership.role == "admin":
            return
        if membership.role != "trainer":
            raise PermissionDenied("Only trainers or admins can manage grades.")
        try:
            from apps.trainers.services import TrainerService

            trainer = TrainerService.get_trainer_by_user(user, membership.institution)
        except NotFound:
            raise PermissionDenied("No trainer profile found for your account.")

        if str(enrollment.class_instance.trainer_id) != str(trainer.id):
            raise PermissionDenied("You can only manage grades for your own classes.")

    @staticmethod
    def launch_grade(
        user,
        membership,
        enrollment_id: str,
        institution,
        assessment_type: str,
        value: Decimal,
        max_value: Decimal,
        assessed_at,
        notes: str = "",
    ) -> Grade:
        """
        Launch a grade for an enrollment.
        Validates:
          - enrollment belongs to the institution
          - enrollment is active
          - trainer owns the class (or user is admin)
          - value does not exceed max_value
          - no duplicate assessment_type for this enrollment
        """
        try:
            enrollment = Enrollment.objects.select_related(
                "class_instance__trainer",
                "class_instance__institution",
                "student",
            ).get(id=enrollment_id, class_instance__institution=institution)
        except Enrollment.DoesNotExist:
            raise NotFound("Enrollment not found.")

        if enrollment.status != Enrollment.Status.ACTIVE:
            raise ValidationError(
                {"enrollment": f"Cannot grade a {enrollment.status} enrollment."}
            )

        GradeService._validate_trainer_owns_class(user, membership, enrollment)

        if value > max_value:
            raise ValidationError({"value": "Grade value cannot exceed max_value."})

        if Grade.objects.filter(
            enrollment=enrollment,
            assessment_type=assessment_type,
        ).exists():
            raise ValidationError(
                {
                    "assessment_type": f'A grade of type "{assessment_type}" already exists for this enrollment.'
                }
            )

        try:
            grade = Grade.objects.create(
                institution=institution,
                enrollment=enrollment,
                assessment_type=assessment_type,
                value=value,
                max_value=max_value,
                assessed_at=assessed_at,
                notes=notes,
            )
        except IntegrityError:
            raise ValidationError(
                {
                    "assessment_type": f'A grade of type "{assessment_type}" already exists for this enrollment.'
                }
            )

        from apps.notifications.services import NotificationService
        NotificationService.notify_grade(grade)

        return grade

    @staticmethod
    def get_grade(grade_id: str, institution) -> Grade:
        try:
            return Grade.objects.select_related(
                "enrollment__student",
                "enrollment__class_instance__course",
                "enrollment__class_instance__trainer",
            ).get(id=grade_id, institution=institution)
        except Grade.DoesNotExist:
            raise NotFound("Grade not found.")

    @staticmethod
    def update_grade(user, membership, grade: Grade, data: dict) -> Grade:
        """
        Update an existing grade.
        Trainer ownership re-validated on every update.
        """
        GradeService._validate_trainer_owns_class(user, membership, grade.enrollment)

        allowed = {"value", "max_value", "assessed_at", "notes"}
        for field, value in data.items():
            if field in allowed:
                setattr(grade, field, value)

        new_value = data.get("value", grade.value)
        new_max_value = data.get("max_value", grade.max_value)
        if new_value > new_max_value:
            raise ValidationError({"value": "Grade value cannot exceed max_value."})

        grade.save()
        return grade

    @staticmethod
    def delete_grade(user, membership, grade: Grade) -> None:
        GradeService._validate_trainer_owns_class(user, membership, grade.enrollment)
        grade.delete()

    @staticmethod
    def list_grades(
        institution,
        enrollment_id: str = None,
        class_id: str = None,
        student_id: str = None,
        assessment_type: str = None,
    ):
        qs = Grade.objects.select_related(
            "enrollment__student",
            "enrollment__class_instance__course",
        ).filter(institution=institution)

        if enrollment_id:
            qs = qs.filter(enrollment_id=enrollment_id)
        if class_id:
            qs = qs.filter(enrollment__class_instance_id=class_id)
        if student_id:
            qs = qs.filter(enrollment__student_id=student_id)
        if assessment_type:
            qs = qs.filter(assessment_type=assessment_type)

        return qs.order_by("-assessed_at")

    @staticmethod
    def get_grades_for_student(student) -> list:
        """
        Return all grades for a student, grouped by enrollment/class.
        Used by the student /my-grades/ endpoint.
        """
        return (
            Grade.objects.select_related(
                "enrollment__class_instance__course",
                "enrollment__class_instance__trainer",
            )
            .filter(
                enrollment__student=student,
                enrollment__status=Enrollment.Status.ACTIVE,
            )
            .order_by(
                "enrollment__class_instance__name",
                "assessment_type",
            )
        )

    @staticmethod
    def calculate_average(enrollment: Enrollment) -> Decimal:
        """
        Calculate the weighted average for an enrollment.
        Each grade contributes proportionally: (value / max_value) * 20.
        Final result normalised to a 0–20 scale, rounded to 2 decimal places.
        """
        grades = Grade.objects.filter(enrollment=enrollment)
        if not grades.exists():
            return Decimal("0.00")

        total_weighted = Decimal("0")
        count = 0
        for grade in grades:
            if grade.max_value > 0:
                normalised = (grade.value / grade.max_value) * Decimal("20")
                total_weighted += normalised
                count += 1

        if count == 0:
            return Decimal("0.00")

        avg = total_weighted / count
        return avg.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def get_class_report(class_id: str, institution) -> list:
        """
        Build a full grade report for a class.
        Returns a list of dicts, one per active enrollment,
        each containing student info, all grades, and calculated average.
        """
        from apps.classes.models import Class

        try:
            class_instance = Class.objects.get(id=class_id, institution=institution)
        except Class.DoesNotExist:
            raise NotFound("Class not found.")

        enrollments = (
            Enrollment.objects.select_related("student")
            .filter(
                class_instance=class_instance,
            )
            .order_by("student__full_name")
        )

        report = []
        for enrollment in enrollments:
            grades = Grade.objects.filter(enrollment=enrollment).order_by(
                "assessment_type"
            )
            average = GradeService.calculate_average(enrollment)
            report.append(
                {
                    "enrollment_id": str(enrollment.id),
                    "enrollment_status": enrollment.status,
                    "student": {
                        "id": str(enrollment.student.id),
                        "full_name": enrollment.student.full_name,
                        "student_code": enrollment.student.student_code,
                    },
                    "grades": grades,
                    "average": average,
                }
            )

        return report
