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
            student = Student.objects.create(
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
        return student

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
        qs = Student.objects.select_related("user").filter(institution=institution)
        if search:
            qs = qs.filter(full_name__icontains=search) | qs.filter(
                student_code__icontains=search
            )
            qs = qs.filter(institution=institution)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs.order_by("full_name")

    @staticmethod
    def get_student_by_user(user) -> Student:
        try:
            return Student.objects.select_related("institution").get(user=user)
        except Student.DoesNotExist:
            raise NotFound("Student profile not found for this user.")

    @staticmethod
    def link_user(student: Student, user) -> Student:
        """Link a User account to a Student profile."""
        if student.institution_id != user.institution_id:
            raise ValidationError(
                {"user": "User must belong to the same institution as the student."}
            )
        if user.role != "student":
            raise ValidationError(
                {
                    "user": 'Only users with role "student" can be linked to a student profile.'
                }
            )
        if Student.objects.filter(user=user).exclude(id=student.id).exists():
            raise ValidationError(
                {"user": "This user is already linked to another student profile."}
            )
        student.user = user
        student.save()
        return student
