"""
HTTP-layer tests for grades endpoints.
"""

import pytest
from decimal import Decimal
from datetime import date

from conftest import (
    InstitutionFactory, UserFactory, MembershipFactory,
    TrainerFactory, StudentFactory, ClassFactory,
    EnrollmentFactory, GradeFactory, make_auth_client,
)


@pytest.fixture
def grade_setup(db, institution, admin_user):
    """Creates trainer + student + class + enrollment for grade tests."""
    trainer = TrainerFactory(institution=institution)
    student = StudentFactory(institution=institution)
    class_inst = ClassFactory(institution=institution, trainer=trainer)
    enrollment = EnrollmentFactory(class_instance=class_inst, student=student)
    return {
        "institution": institution,
        "admin_user": admin_user,
        "trainer": trainer,
        "student": student,
        "class_inst": class_inst,
        "enrollment": enrollment,
    }


@pytest.mark.django_db
class TestGradeListCreateView:

    URL = "/api/grades/"

    def test_unauthenticated_returns_401(self, client):
        assert client.get(self.URL).status_code == 401

    def test_student_cannot_list(self, db, institution, student_user):
        resp = make_auth_client(student_user, institution).get(self.URL)
        assert resp.status_code == 403

    def test_admin_can_list(self, db, grade_setup):
        gs = grade_setup
        GradeFactory(institution=gs["institution"], enrollment=gs["enrollment"])
        resp = make_auth_client(gs["admin_user"], gs["institution"]).get(self.URL)
        assert resp.status_code == 200
        assert resp.json()["count"] >= 1

    def test_admin_can_create_grade(self, db, grade_setup):
        gs = grade_setup
        resp = make_auth_client(gs["admin_user"], gs["institution"]).post(self.URL, {
            "enrollment_id": str(gs["enrollment"].id),
            "assessment_type": "exam",
            "value": "16.00",
            "max_value": "20.00",
            "assessed_at": str(date.today()),
        })
        assert resp.status_code == 201
        assert Decimal(resp.json()["value"]) == Decimal("16.00")

    def test_grades_scoped_to_institution(self, db, grade_setup):
        gs = grade_setup
        # Grade in another institution — should not be visible
        other = EnrollmentFactory(
            class_instance=ClassFactory(institution=InstitutionFactory()),
            student=StudentFactory(institution=InstitutionFactory()),
        )
        GradeFactory(institution=other.class_instance.institution, enrollment=other)
        GradeFactory(institution=gs["institution"], enrollment=gs["enrollment"])

        resp = make_auth_client(gs["admin_user"], gs["institution"]).get(self.URL)
        assert resp.json()["count"] == 1


@pytest.mark.django_db
class TestGradeDetailView:

    def _url(self, grade_id):
        return f"/api/grades/{grade_id}/"

    def test_admin_get_grade(self, db, grade_setup):
        gs = grade_setup
        grade = GradeFactory(institution=gs["institution"], enrollment=gs["enrollment"])
        resp = make_auth_client(gs["admin_user"], gs["institution"]).get(self._url(grade.id))
        assert resp.status_code == 200
        assert resp.json()["id"] == str(grade.id)

    def test_student_cannot_get(self, db, institution, student_user, grade):
        resp = make_auth_client(student_user, institution).get(self._url(grade.id))
        assert resp.status_code == 403

    def test_admin_patch_grade(self, db, grade_setup):
        gs = grade_setup
        grade = GradeFactory(institution=gs["institution"], enrollment=gs["enrollment"])
        resp = make_auth_client(gs["admin_user"], gs["institution"]).patch(
            self._url(grade.id), {"value": "18.00"},
            format='json',
        )
        assert resp.status_code == 200
        assert Decimal(resp.json()["value"]) == Decimal("18.00")

    def test_admin_delete_grade(self, db, grade_setup):
        gs = grade_setup
        grade = GradeFactory(institution=gs["institution"], enrollment=gs["enrollment"])
        resp = make_auth_client(gs["admin_user"], gs["institution"]).delete(self._url(grade.id))
        assert resp.status_code == 204

    def test_cannot_access_other_institution_grade(self, db, institution, admin_user):
        other_enroll = EnrollmentFactory(
            class_instance=ClassFactory(institution=InstitutionFactory()),
        )
        other_grade = GradeFactory(
            institution=other_enroll.class_instance.institution,
            enrollment=other_enroll,
        )
        resp = make_auth_client(admin_user, institution).get(self._url(other_grade.id))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestGradeReportView:

    URL = "/api/grades/report/"

    def test_missing_class_id_returns_400(self, db, institution, admin_user):
        resp = make_auth_client(admin_user, institution).get(self.URL)
        assert resp.status_code == 400

    def test_admin_can_get_report(self, db, grade_setup):
        gs = grade_setup
        GradeFactory(institution=gs["institution"], enrollment=gs["enrollment"])
        resp = make_auth_client(gs["admin_user"], gs["institution"]).get(
            self.URL, {"class_id": str(gs["class_inst"].id)}
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_student_cannot_get_report(self, db, institution, student_user, class_instance):
        resp = make_auth_client(student_user, institution).get(
            self.URL, {"class_id": str(class_instance.id)}
        )
        assert resp.status_code == 403


@pytest.mark.django_db
class TestMyGradesView:

    URL = "/api/grades/my-grades/"

    def test_student_sees_own_grades(self, db, institution):
        user = UserFactory()
        MembershipFactory(user=user, institution=institution, role="student")
        student = StudentFactory(institution=institution, user=user)
        class_inst = ClassFactory(institution=institution)
        enrollment = EnrollmentFactory(class_instance=class_inst, student=student)
        GradeFactory(institution=institution, enrollment=enrollment)

        resp = make_auth_client(user, institution).get(self.URL)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_trainer_without_student_profile_gets_404(self, db, institution, trainer_user):
        resp = make_auth_client(trainer_user, institution).get(self.URL)
        assert resp.status_code == 404
