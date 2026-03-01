from django.db import IntegrityError
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from .models import Class, Enrollment


class ClassService:

    @staticmethod
    def create_class(
        institution, course, trainer, name: str, start_date, end_date, **kwargs
    ) -> Class:
        """
        Create a class. Validates that course and trainer belong
        to the same institution as the class being created.
        """
        if course.institution_id != institution.id:
            raise ValidationError(
                {"course": "Course does not belong to this institution."}
            )
        if trainer.institution_id != institution.id:
            raise ValidationError(
                {"trainer": "Trainer does not belong to this institution."}
            )
        if start_date >= end_date:
            raise ValidationError({"end_date": "End date must be after start date."})

        class_instance = Class.objects.create(
            institution=institution,
            course=course,
            trainer=trainer,
            name=name,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )
        return class_instance

    @staticmethod
    def get_class(class_id: str, institution) -> Class:
        try:
            return Class.objects.select_related("course", "trainer", "institution").get(
                id=class_id, institution=institution
            )
        except Class.DoesNotExist:
            raise NotFound("Class not found.")

    @staticmethod
    def update_class(class_instance: Class, data: dict) -> Class:
        allowed = {"name", "status", "start_date", "end_date", "trainer"}

        if "start_date" in data or "end_date" in data:
            start = data.get("start_date", class_instance.start_date)
            end = data.get("end_date", class_instance.end_date)
            if start >= end:
                raise ValidationError(
                    {"end_date": "End date must be after start date."}
                )

        if class_instance.is_closed and "status" not in data:
            raise ValidationError({"status": "Cannot update a closed class."})

        for field, value in data.items():
            if field in allowed:
                setattr(class_instance, field, value)

        class_instance.save()
        return class_instance

    @staticmethod
    def close_class(class_instance: Class) -> Class:
        """
        Close a class and mark all active enrollments as completed.
        """
        if class_instance.is_closed:
            raise ValidationError({"status": "Class is already closed."})

        class_instance.status = Class.Status.CLOSED
        class_instance.save()

        Enrollment.objects.filter(
            class_instance=class_instance,
            status=Enrollment.Status.ACTIVE,
        ).update(status=Enrollment.Status.COMPLETED)

        return class_instance

    @staticmethod
    def delete_class(class_instance: Class) -> None:
        """
        Only open classes with no enrollments can be hard-deleted.
        Anything else must be closed instead.
        """
        if class_instance.enrollments.exists():
            raise ValidationError(
                {
                    "detail": "Cannot delete a class with enrolled students. Close it instead."
                }
            )
        class_instance.delete()

    @staticmethod
    def list_classes(
        institution,
        status: str = None,
        course_id: str = None,
        trainer_id: str = None,
        search: str = None,
    ):
        qs = Class.objects.select_related("course", "trainer", "institution").filter(
            institution=institution
        )

        if status:
            qs = qs.filter(status=status)
        if course_id:
            qs = qs.filter(course_id=course_id)
        if trainer_id:
            qs = qs.filter(trainer_id=trainer_id)
        if search:
            qs = qs.filter(name__icontains=search)

        return qs.order_by("-start_date")

    @staticmethod
    def list_classes_for_trainer(trainer) -> list:
        return (
            Class.objects.select_related("course", "institution")
            .filter(trainer=trainer)
            .order_by("-start_date")
        )

    @staticmethod
    def list_classes_for_student(student) -> list:
        return (
            Class.objects.select_related("course", "trainer", "institution")
            .filter(
                enrollments__student=student,
                enrollments__status=Enrollment.Status.ACTIVE,
            )
            .order_by("-start_date")
        )


class EnrollmentService:

    @staticmethod
    def enroll_student(class_instance: Class, student) -> Enrollment:
        """
        Enroll a student in a class.
        Validates: class is open, student belongs to same institution,
        student not already enrolled.
        """
        if not class_instance.is_open:
            raise ValidationError(
                {
                    "detail": f'Cannot enroll in a class with status "{class_instance.status}".'
                }
            )
        if student.institution_id != class_instance.institution_id:
            raise ValidationError(
                {"student": "Student does not belong to this institution."}
            )
        if Enrollment.objects.filter(
            class_instance=class_instance,
            student=student,
        ).exists():
            raise ValidationError(
                {"student": "This student is already enrolled in this class."}
            )
        try:
            enrollment = Enrollment.objects.create(
                class_instance=class_instance,
                student=student,
            )
        except IntegrityError:
            raise ValidationError(
                {"student": "This student is already enrolled in this class."}
            )
        return enrollment

    @staticmethod
    def get_enrollment(enrollment_id: str, institution) -> Enrollment:
        try:
            return Enrollment.objects.select_related(
                "class_instance__institution",
                "student",
            ).get(id=enrollment_id, class_instance__institution=institution)
        except Enrollment.DoesNotExist:
            raise NotFound("Enrollment not found.")

    @staticmethod
    def drop_enrollment(enrollment: Enrollment) -> Enrollment:
        if enrollment.status == Enrollment.Status.COMPLETED:
            raise ValidationError({"detail": "Cannot drop a completed enrollment."})
        if enrollment.status == Enrollment.Status.DROPPED:
            raise ValidationError({"detail": "Enrollment is already dropped."})
        enrollment.status = Enrollment.Status.DROPPED
        enrollment.save()
        return enrollment

    @staticmethod
    def list_enrollments(class_instance: Class, status: str = None):
        qs = Enrollment.objects.select_related("student").filter(
            class_instance=class_instance
        )
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("student__full_name")

    @staticmethod
    def list_enrollments_for_student(student, status: str = None):
        qs = Enrollment.objects.select_related(
            "class_instance__course",
            "class_instance__trainer",
        ).filter(student=student)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-enrolled_at")
