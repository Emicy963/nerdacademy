"""
Tests for ClassService and EnrollmentService: lifecycle, enrolment,
drop, close, delete, multi-tenant isolation.
"""

import pytest
from datetime import date, timedelta
from rest_framework.exceptions import ValidationError, NotFound

from apps.classes.services import ClassService, EnrollmentService
from apps.classes.models import Class, Enrollment
from conftest import (
    InstitutionFactory,
    ClassFactory,
    StudentFactory,
    TrainerFactory,
    CourseFactory,
    EnrollmentFactory,
)

# ── Helpers ────────────────────────────────────────────────────────


def tomorrow():
    return date.today() + timedelta(days=1)


def next_month():
    return date.today() + timedelta(days=30)


# ══════════════════════════════════════════════════════════════════
#  ClassService
# ══════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestClassServiceCreate:

    def test_create_class_success(self, institution, course, trainer):
        course.institution = institution
        course.save()
        trainer.institution = institution
        trainer.save()
        cls = ClassService.create_class(
            institution=institution,
            course=course,
            trainer=trainer,
            name="Turma A",
            start_date=date.today(),
            end_date=next_month(),
        )
        assert cls.name == "Turma A"
        assert cls.status == Class.Status.OPEN
        assert cls.institution == institution

    def test_create_class_end_before_start_raises(self, institution, course, trainer):
        course.institution = institution
        course.save()
        trainer.institution = institution
        trainer.save()
        with pytest.raises(ValidationError) as exc:
            ClassService.create_class(
                institution=institution,
                course=course,
                trainer=trainer,
                name="Turma B",
                start_date=next_month(),
                end_date=date.today(),
            )
        assert "end_date" in exc.value.detail

    def test_create_class_course_wrong_institution(self, db):
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        course = CourseFactory(institution=inst_b)
        trainer = TrainerFactory(institution=inst_a)
        with pytest.raises(ValidationError) as exc:
            ClassService.create_class(
                institution=inst_a,
                course=course,
                trainer=trainer,
                name="Turma X",
                start_date=date.today(),
                end_date=next_month(),
            )
        assert "course" in exc.value.detail

    def test_create_class_trainer_wrong_institution(self, db):
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        course = CourseFactory(institution=inst_a)
        trainer = TrainerFactory(institution=inst_b)
        with pytest.raises(ValidationError) as exc:
            ClassService.create_class(
                institution=inst_a,
                course=course,
                trainer=trainer,
                name="Turma X",
                start_date=date.today(),
                end_date=next_month(),
            )
        assert "trainer" in exc.value.detail


@pytest.mark.django_db
class TestClassServiceGet:

    def test_get_class_success(self, institution, class_instance):
        found = ClassService.get_class(str(class_instance.id), institution)
        assert found.id == class_instance.id

    def test_get_class_wrong_institution(self, class_instance):
        other = InstitutionFactory()
        with pytest.raises(NotFound):
            ClassService.get_class(str(class_instance.id), other)


@pytest.mark.django_db
class TestClassServiceUpdate:

    def test_update_name(self, institution, class_instance):
        updated = ClassService.update_class(class_instance, {"name": "Turma B"})
        assert updated.name == "Turma B"

    def test_update_closed_class_raises(self, institution, class_instance):
        ClassService.close_class(class_instance)
        with pytest.raises(ValidationError):
            ClassService.update_class(class_instance, {"name": "Novo Nome"})

    def test_update_invalid_dates_raises(self, institution, class_instance):
        with pytest.raises(ValidationError) as exc:
            ClassService.update_class(
                class_instance,
                {
                    "start_date": next_month(),
                    "end_date": date.today(),
                },
            )
        assert "end_date" in exc.value.detail


@pytest.mark.django_db
class TestClassServiceClose:

    def test_close_class_marks_closed(self, institution, class_instance, enrollment):
        closed = ClassService.close_class(class_instance)
        assert closed.status == Class.Status.CLOSED

    def test_close_class_completes_active_enrollments(
        self, institution, class_instance, enrollment
    ):
        assert enrollment.status == Enrollment.Status.ACTIVE
        ClassService.close_class(class_instance)
        enrollment.refresh_from_db()
        assert enrollment.status == Enrollment.Status.COMPLETED

    def test_close_already_closed_raises(self, institution, class_instance):
        ClassService.close_class(class_instance)
        with pytest.raises(ValidationError) as exc:
            ClassService.close_class(class_instance)
        assert "status" in exc.value.detail


@pytest.mark.django_db
class TestClassServiceDelete:

    def test_delete_empty_class_success(self, institution, class_instance):
        class_id = class_instance.id
        ClassService.delete_class(class_instance)
        assert not Class.objects.filter(id=class_id).exists()

    def test_delete_class_with_enrollments_raises(
        self, institution, class_instance, enrollment
    ):
        with pytest.raises(ValidationError) as exc:
            ClassService.delete_class(class_instance)
        assert "detail" in exc.value.detail


# ══════════════════════════════════════════════════════════════════
#  EnrollmentService
# ══════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestEnrollmentServiceEnroll:

    def test_enroll_student_success(self, institution, class_instance, student):
        student.institution = institution
        student.save()
        enr = EnrollmentService.enroll_student(class_instance, student)
        assert enr.student == student
        assert enr.status == Enrollment.Status.ACTIVE

    def test_enroll_in_closed_class_raises(self, institution, class_instance, student):
        student.institution = institution
        student.save()
        ClassService.close_class(class_instance)
        with pytest.raises(ValidationError) as exc:
            EnrollmentService.enroll_student(class_instance, student)
        assert "detail" in exc.value.detail

    def test_enroll_student_wrong_institution(self, institution, class_instance):
        other = InstitutionFactory()
        student = StudentFactory(institution=other)
        with pytest.raises(ValidationError) as exc:
            EnrollmentService.enroll_student(class_instance, student)
        assert "student" in exc.value.detail

    def test_enroll_duplicate_raises(self, institution, class_instance, student):
        student.institution = institution
        student.save()
        EnrollmentService.enroll_student(class_instance, student)
        with pytest.raises(ValidationError) as exc:
            EnrollmentService.enroll_student(class_instance, student)
        assert "student" in exc.value.detail


@pytest.mark.django_db
class TestEnrollmentServiceDrop:

    def test_drop_active_enrollment(self, institution, enrollment):
        dropped = EnrollmentService.drop_enrollment(enrollment)
        assert dropped.status == Enrollment.Status.DROPPED

    def test_drop_completed_enrollment_raises(
        self, institution, class_instance, enrollment
    ):
        ClassService.close_class(class_instance)
        enrollment.refresh_from_db()
        with pytest.raises(ValidationError) as exc:
            EnrollmentService.drop_enrollment(enrollment)
        assert "detail" in exc.value.detail

    def test_drop_already_dropped_raises(self, institution, enrollment):
        EnrollmentService.drop_enrollment(enrollment)
        enrollment.refresh_from_db()
        with pytest.raises(ValidationError) as exc:
            EnrollmentService.drop_enrollment(enrollment)
        assert "detail" in exc.value.detail


@pytest.mark.django_db
class TestEnrollmentServiceList:

    def test_list_enrollments_for_class(self, institution, class_instance, student):
        student.institution = institution
        student.save()
        enr = EnrollmentService.enroll_student(class_instance, student)
        result = list(EnrollmentService.list_enrollments(class_instance))
        assert enr in result

    def test_list_enrollments_filter_by_status(
        self, institution, class_instance, student
    ):
        student.institution = institution
        student.save()
        enr = EnrollmentService.enroll_student(class_instance, student)
        EnrollmentService.drop_enrollment(enr)
        active = list(
            EnrollmentService.list_enrollments(class_instance, status="active")
        )
        assert enr not in active
