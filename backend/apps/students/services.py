from django.db import IntegrityError
from rest_framework.exceptions import ValidationError, NotFound

from .models import Student


class StudentService:

    @staticmethod
    def create_student(
        institution, full_name: str, student_code: str, **kwargs
    ) -> Student:
        if Student.objects.filter(
            institution=institution, student_code=student_code
        ).exists():
            raise ValidationError(
                {
                    "student_code": "This student code is already in use for this institution."
                }
            )
        try:
            return Student.objects.create(
                institution=institution,
                full_name=full_name,
                student_code=student_code,
                **kwargs,
            )
        except IntegrityError:
            raise ValidationError(
                {
                    "student_code": "This student code is already in use for this institution."
                }
            )

    @staticmethod
    def get_student(student_id: str, institution) -> Student:
        try:
            return Student.objects.select_related("institution", "user").get(
                id=student_id,
                institution=institution,
            )
        except Student.DoesNotExist:
            raise NotFound("Student not found.")

    @staticmethod
    def update_student(student: Student, data: dict) -> Student:
        allowed = {"full_name", "birth_date", "phone", "address", "is_active"}
        for field, value in data.items():
            if field in allowed:
                setattr(student, field, value)
        student.save()
        return student

    @staticmethod
    def deactivate_student(student: Student) -> Student:
        student.is_active = False
        student.save()
        return student

    @staticmethod
    def list_students(institution, search: str = None, is_active: bool = None):
        from django.db.models import Q

        qs = Student.objects.select_related("user").filter(institution=institution)
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search) | Q(student_code__icontains=search)
            )
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs.order_by("full_name")

    @staticmethod
    def get_student_by_user(user, institution) -> Student:
        """
        Get the student profile for a user within a specific institution.
        A user can be a student at multiple institutions.
        """
        try:
            return Student.objects.select_related("institution").get(
                user=user,
                institution=institution,
            )
        except Student.DoesNotExist:
            raise NotFound(
                "Student profile not found for this user at this institution."
            )

    @staticmethod
    def link_user(student: Student, user, membership) -> Student:
        """
        Link a User account to a Student profile.
        Validates via Membership that the user has a student role
        at this institution.
        """
        if membership.institution_id != student.institution_id:
            raise ValidationError(
                {
                    "user": "User must have a membership at the same institution as the student."
                }
            )
        if membership.role != "student":
            raise ValidationError(
                {
                    "user": 'Only users with role "student" can be linked to a student profile.'
                }
            )
        if (
            Student.objects.filter(user=user, institution=student.institution)
            .exclude(id=student.id)
            .exists()
        ):
            raise ValidationError(
                {
                    "user": "This user is already linked to another student profile at this institution."
                }
            )
        student.user = user
        student.save()
        return student
