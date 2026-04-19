"""
Tests for GradeService with Membership-based architecture.
"""

import pytest
from decimal import Decimal
from datetime import date

from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from apps.grades.services import GradeService
from apps.classes.services import ClassService, EnrollmentService
from apps.classes.models import Enrollment
from apps.accounts.models import Membership
from conftest import (
    InstitutionFactory,
    GradeFactory,
    EnrollmentFactory,
    ClassFactory,
    StudentFactory,
    TrainerFactory,
    CourseFactory,
    UserFactory,
    MembershipFactory,
)

# ── Helpers ────────────────────────────────────────────────────────


def make_admin(institution):
    """Create a user + admin membership and return (user, membership)."""
    user = UserFactory()
    m = MembershipFactory(user=user, institution=institution, role="admin")
    return user, m


def make_trainer_with_profile(institution):
    """Create user + trainer membership + trainer profile."""
    user = UserFactory()
    membership = MembershipFactory(user=user, institution=institution, role="trainer")
    from apps.trainers.services import TrainerService

    trainer = TrainerFactory(institution=institution)
    TrainerService.link_user(trainer, user, membership)
    return user, membership, trainer


# ══════════════════════════════════════════════════════════════════
#  Launch grade
# ══════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestGradeServiceLaunch:

    def test_launch_grade_as_admin(self, institution, enrollment):
        admin, membership = make_admin(institution)
        grade = GradeService.launch_grade(
            user=admin,
            membership=membership,
            enrollment_id=str(enrollment.id),
            institution=institution,
            assessment_type="exam",
            value=Decimal("15.00"),
            max_value=Decimal("20.00"),
            assessed_at=date.today(),
        )
        assert grade.value == Decimal("15.00")
        assert grade.assessment_type == "exam"
        assert grade.institution == institution

    def test_launch_grade_as_trainer_owner(self, institution, class_instance, student):
        user, membership, trainer = make_trainer_with_profile(institution)
        class_instance.trainer = trainer
        class_instance.save()
        student.institution = institution
        student.save()
        enr = EnrollmentService.enroll_student(class_instance, student)

        grade = GradeService.launch_grade(
            user=user,
            membership=membership,
            enrollment_id=str(enr.id),
            institution=institution,
            assessment_type="continuous",
            value=Decimal("18.00"),
            max_value=Decimal("20.00"),
            assessed_at=date.today(),
        )
        assert grade.assessment_type == "continuous"

    def test_launch_grade_trainer_not_owner_raises(
        self, institution, class_instance, student
    ):
        """Trainer not assigned to the class cannot launch grades."""
        other_user, other_membership, _ = make_trainer_with_profile(institution)
        student.institution = institution
        student.save()
        enr = EnrollmentService.enroll_student(class_instance, student)

        with pytest.raises(PermissionDenied):
            GradeService.launch_grade(
                user=other_user,
                membership=other_membership,
                enrollment_id=str(enr.id),
                institution=institution,
                assessment_type="exam",
                value=Decimal("10.00"),
                max_value=Decimal("20.00"),
                assessed_at=date.today(),
            )

    def test_launch_grade_value_exceeds_max_raises(self, institution, enrollment):
        admin, membership = make_admin(institution)
        with pytest.raises(ValidationError) as exc:
            GradeService.launch_grade(
                user=admin,
                membership=membership,
                enrollment_id=str(enrollment.id),
                institution=institution,
                assessment_type="exam",
                value=Decimal("25.00"),
                max_value=Decimal("20.00"),
                assessed_at=date.today(),
            )
        assert "value" in exc.value.detail

    def test_launch_grade_duplicate_type_raises(self, institution, enrollment, grade):
        admin, membership = make_admin(institution)
        with pytest.raises(ValidationError) as exc:
            GradeService.launch_grade(
                user=admin,
                membership=membership,
                enrollment_id=str(enrollment.id),
                institution=institution,
                assessment_type=grade.assessment_type,
                value=Decimal("12.00"),
                max_value=Decimal("20.00"),
                assessed_at=date.today(),
            )
        assert "assessment_type" in exc.value.detail

    def test_launch_grade_dropped_enrollment_raises(
        self, institution, class_instance, student
    ):
        student.institution = institution
        student.save()
        enr = EnrollmentService.enroll_student(class_instance, student)
        EnrollmentService.drop_enrollment(enr)
        enr.refresh_from_db()

        admin, membership = make_admin(institution)
        with pytest.raises(ValidationError) as exc:
            GradeService.launch_grade(
                user=admin,
                membership=membership,
                enrollment_id=str(enr.id),
                institution=institution,
                assessment_type="exam",
                value=Decimal("10.00"),
                max_value=Decimal("20.00"),
                assessed_at=date.today(),
            )
        assert "enrollment" in exc.value.detail


# ══════════════════════════════════════════════════════════════════
#  Update and delete
# ══════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestGradeServiceUpdate:

    def test_update_grade_value(self, institution, enrollment, grade):
        admin, membership = make_admin(institution)
        updated = GradeService.update_grade(
            admin, membership, grade, {"value": Decimal("17.50")}
        )
        assert updated.value == Decimal("17.50")

    def test_update_grade_value_exceeds_max_raises(
        self, institution, enrollment, grade
    ):
        admin, membership = make_admin(institution)
        with pytest.raises(ValidationError) as exc:
            GradeService.update_grade(
                admin,
                membership,
                grade,
                {"value": Decimal("25.00"), "max_value": Decimal("20.00")},
            )
        assert "value" in exc.value.detail

    def test_update_grade_notes(self, institution, enrollment, grade):
        admin, membership = make_admin(institution)
        updated = GradeService.update_grade(
            admin, membership, grade, {"notes": "Boa prestação."}
        )
        assert updated.notes == "Boa prestação."


@pytest.mark.django_db
class TestGradeServiceDelete:

    def test_delete_grade_as_admin(self, institution, enrollment, grade):
        admin, membership = make_admin(institution)
        grade_id = grade.id
        GradeService.delete_grade(admin, membership, grade)
        from apps.grades.models import Grade

        assert not Grade.objects.filter(id=grade_id).exists()


# ══════════════════════════════════════════════════════════════════
#  Average calculation
# ══════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestGradeServiceAverage:

    def test_average_no_grades(self, enrollment):
        avg = GradeService.calculate_average(enrollment)
        assert avg == Decimal("0.00")

    def test_average_full_marks(self, institution, enrollment):
        admin, membership = make_admin(institution)
        GradeService.launch_grade(
            user=admin,
            membership=membership,
            enrollment_id=str(enrollment.id),
            institution=institution,
            assessment_type="exam",
            value=Decimal("20.00"),
            max_value=Decimal("20.00"),
            assessed_at=date.today(),
        )
        avg = GradeService.calculate_average(enrollment)
        assert avg == Decimal("20.00")

    def test_average_half_marks(self, institution, enrollment):
        admin, membership = make_admin(institution)
        GradeService.launch_grade(
            user=admin,
            membership=membership,
            enrollment_id=str(enrollment.id),
            institution=institution,
            assessment_type="exam",
            value=Decimal("10.00"),
            max_value=Decimal("20.00"),
            assessed_at=date.today(),
        )
        avg = GradeService.calculate_average(enrollment)
        assert avg == Decimal("10.00")

    def test_average_multiple_grades_normalised(self, institution, enrollment):
        """
        exam: 16/20 → 16.00 normalised
        continuous: 80/100 → 16.00 normalised
        average → 16.00
        """
        admin, membership = make_admin(institution)
        GradeService.launch_grade(
            user=admin,
            membership=membership,
            enrollment_id=str(enrollment.id),
            institution=institution,
            assessment_type="exam",
            value=Decimal("16.00"),
            max_value=Decimal("20.00"),
            assessed_at=date.today(),
        )
        GradeService.launch_grade(
            user=admin,
            membership=membership,
            enrollment_id=str(enrollment.id),
            institution=institution,
            assessment_type="continuous",
            value=Decimal("80.00"),
            max_value=Decimal("100.00"),
            assessed_at=date.today(),
        )
        avg = GradeService.calculate_average(enrollment)
        assert avg == Decimal("16.00")


# ══════════════════════════════════════════════════════════════════
#  Class report
# ══════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestGradeServiceReport:

    def test_get_class_report_structure(
        self, institution, class_instance, student, enrollment, grade
    ):
        report = GradeService.get_class_report(str(class_instance.id), institution)
        assert len(report) == 1
        row = report[0]
        assert "enrollment_id" in row
        assert "student" in row
        assert "grades" in row
        assert "average" in row
        assert row["student"]["full_name"] == student.full_name

    def test_get_class_report_wrong_institution_raises(self, class_instance):
        other = InstitutionFactory()
        with pytest.raises(NotFound):
            GradeService.get_class_report(str(class_instance.id), other)

    def test_get_class_report_empty_class(self, institution, class_instance):
        report = GradeService.get_class_report(str(class_instance.id), institution)
        assert report == []


# ══════════════════════════════════════════════════════════════════
#  List grades
# ══════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestGradeServiceList:

    def test_list_grades_scoped_to_institution(self, institution, grade):
        result = list(GradeService.list_grades(institution=institution))
        assert all(g.institution_id == institution.id for g in result)

    def test_list_grades_filter_by_assessment_type(self, institution, enrollment):
        admin, membership = make_admin(institution)
        GradeService.launch_grade(
            user=admin,
            membership=membership,
            enrollment_id=str(enrollment.id),
            institution=institution,
            assessment_type="exam",
            value=Decimal("15.00"),
            max_value=Decimal("20.00"),
            assessed_at=date.today(),
        )
        GradeService.launch_grade(
            user=admin,
            membership=membership,
            enrollment_id=str(enrollment.id),
            institution=institution,
            assessment_type="continuous",
            value=Decimal("14.00"),
            max_value=Decimal("20.00"),
            assessed_at=date.today(),
        )
        result = list(
            GradeService.list_grades(institution=institution, assessment_type="exam")
        )
        assert all(g.assessment_type == "exam" for g in result)
