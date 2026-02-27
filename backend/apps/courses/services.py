from django.db import IntegrityError
from rest_framework.exceptions import ValidationError, NotFound

from .models import Course


class CourseService:

    @staticmethod
    def create_course(institution, name: str, code: str, **kwargs) -> Course:
        code = code.strip().upper()
        if Course.objects.filter(institution=institution, code=code).exists():
            raise ValidationError(
                {
                    "code": f'A course with code "{code}" already exists in this institution.'
                }
            )
        try:
            course = Course.objects.create(
                institution=institution,
                name=name,
                code=code,
                **kwargs,
            )
        except IntegrityError:
            raise ValidationError(
                {
                    "code": f'A course with code "{code}" already exists in this institution.'
                }
            )
        return course

    @staticmethod
    def get_course(course_id: str, institution) -> Course:
        try:
            return Course.objects.get(id=course_id, institution=institution)
        except Course.DoesNotExist:
            raise NotFound("Course not found.")

    @staticmethod
    def update_course(course: Course, data: dict) -> Course:
        allowed = {"name", "description", "total_hours", "is_active"}
        for field, value in data.items():
            if field in allowed:
                setattr(course, field, value)
        course.save()
        return course

    @staticmethod
    def deactivate_course(course: Course) -> Course:
        """
        Soft-delete: marks course as inactive.
        Does not touch existing classes — they remain in their current state.
        """
        course.is_active = False
        course.save()
        return course

    @staticmethod
    def list_courses(institution, search: str = None, is_active: bool = None):
        qs = Course.objects.filter(institution=institution)
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(code__icontains=search)
            qs = qs.filter(institution=institution)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs.order_by("name")

    @staticmethod
    def get_course_classes(course: Course):
        """Return all classes for this course, ordered by start date descending."""
        return course.classes.select_related("trainer", "institution").order_by(
            "-start_date"
        )
