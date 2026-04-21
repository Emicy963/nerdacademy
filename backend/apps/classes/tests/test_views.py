"""
HTTP-layer tests for classes and enrollments endpoints.
"""

import pytest
from conftest import (
    InstitutionFactory, UserFactory, MembershipFactory,
    ClassFactory, StudentFactory, TrainerFactory,
    EnrollmentFactory, make_auth_client,
)


@pytest.mark.django_db
class TestClassListCreateView:

    URL = "/api/classes/"

    def test_unauthenticated_returns_401(self, client):
        assert client.get(self.URL).status_code == 401

    def test_admin_sees_all_classes(self, db, institution, admin_user, class_instance):
        resp = make_auth_client(admin_user, institution).get(self.URL)
        assert resp.status_code == 200
        assert resp.json()["count"] >= 1

    def test_list_scoped_to_institution(self, db, institution, admin_user):
        ClassFactory.create_batch(2, institution=institution)
        ClassFactory.create_batch(3, institution=InstitutionFactory())
        resp = make_auth_client(admin_user, institution).get(self.URL)
        assert resp.json()["count"] == 2

    def test_trainer_sees_only_own_classes(self, db, institution):
        user = UserFactory()
        MembershipFactory(user=user, institution=institution, role="trainer")
        trainer = TrainerFactory(institution=institution, user=user)
        other_trainer = TrainerFactory(institution=institution)

        # One class for this trainer, one for another
        ClassFactory(institution=institution, trainer=trainer)
        ClassFactory(institution=institution, trainer=other_trainer)

        resp = make_auth_client(user, institution).get(self.URL)
        assert resp.status_code == 200
        assert resp.json()["count"] == 1

    def test_admin_can_create_class(self, db, institution, admin_user, course, trainer):
        from datetime import date, timedelta
        resp = make_auth_client(admin_user, institution).post(self.URL, {
            "name": "Turma A",
            "course_id": str(course.id),
            "trainer_id": str(trainer.id),
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=90)),
        })
        assert resp.status_code == 201

    def test_trainer_cannot_create_class(self, db, institution, trainer_user, course, trainer):
        from datetime import date, timedelta
        resp = make_auth_client(trainer_user, institution).post(self.URL, {
            "name": "Turma X",
            "course_id": str(course.id),
            "trainer_id": str(trainer.id),
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=90)),
        })
        assert resp.status_code == 403


@pytest.mark.django_db
class TestClassDetailView:

    def _url(self, class_id):
        return f"/api/classes/{class_id}/"

    def test_admin_get_detail(self, db, institution, admin_user, class_instance):
        resp = make_auth_client(admin_user, institution).get(self._url(class_instance.id))
        assert resp.status_code == 200

    def test_admin_patch(self, db, institution, admin_user, class_instance):
        resp = make_auth_client(admin_user, institution).patch(
            self._url(class_instance.id), {"name": "Turma B"},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Turma B"

    def test_cannot_access_other_institution_class(self, db, institution, admin_user):
        other_class = ClassFactory(institution=InstitutionFactory())
        resp = make_auth_client(admin_user, institution).get(self._url(other_class.id))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestClassCloseView:

    def _url(self, class_id):
        return f"/api/classes/{class_id}/close/"

    def test_admin_can_close(self, db, institution, admin_user, class_instance):
        resp = make_auth_client(admin_user, institution).post(self._url(class_instance.id))
        assert resp.status_code == 200
        assert resp.json()["status"] == "closed"

    def test_trainer_cannot_close(self, db, institution, trainer_user, class_instance):
        resp = make_auth_client(trainer_user, institution).post(self._url(class_instance.id))
        assert resp.status_code == 403


@pytest.mark.django_db
class TestEnrollmentListCreateView:

    def _url(self, class_id):
        return f"/api/classes/{class_id}/enrollments/"

    def test_admin_can_list_enrollments(self, db, institution, admin_user, class_instance, enrollment):
        resp = make_auth_client(admin_user, institution).get(self._url(class_instance.id))
        assert resp.status_code == 200
        assert resp.json()["count"] == 1

    def test_admin_can_enroll_student(self, db, institution, admin_user, class_instance, student):
        resp = make_auth_client(admin_user, institution).post(
            self._url(class_instance.id), {"student_id": str(student.id)}
        )
        assert resp.status_code == 201

    def test_trainer_cannot_enroll(self, db, institution, trainer_user, class_instance, student):
        resp = make_auth_client(trainer_user, institution).post(
            self._url(class_instance.id), {"student_id": str(student.id)}
        )
        assert resp.status_code == 403

    def test_student_cannot_list_enrollments(self, db, institution, student_user, class_instance):
        resp = make_auth_client(student_user, institution).get(self._url(class_instance.id))
        assert resp.status_code == 403
