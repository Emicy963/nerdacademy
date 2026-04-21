"""
HTTP-layer tests for students endpoints.
"""

import pytest
from conftest import (
    InstitutionFactory, UserFactory, MembershipFactory,
    StudentFactory, make_auth_client,
)


@pytest.mark.django_db
class TestStudentListCreateView:

    URL = "/api/students/"

    def test_unauthenticated_returns_401(self, client):
        resp = client.get(self.URL)
        assert resp.status_code == 401

    def test_student_role_cannot_list(self, db, institution, student_user):
        client = make_auth_client(student_user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 403

    def test_admin_can_list(self, db, institution, admin_user):
        StudentFactory.create_batch(3, institution=institution)
        client = make_auth_client(admin_user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert resp.json()["count"] == 3

    def test_trainer_can_list(self, db, institution, trainer_user):
        StudentFactory.create_batch(2, institution=institution)
        client = make_auth_client(trainer_user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert resp.json()["count"] == 2

    def test_list_scoped_to_institution(self, db, institution, admin_user):
        StudentFactory.create_batch(2, institution=institution)
        StudentFactory.create_batch(5, institution=InstitutionFactory())
        client = make_auth_client(admin_user, institution)
        resp = client.get(self.URL)
        assert resp.json()["count"] == 2

    def test_admin_can_create_student(self, db, institution, admin_user):
        client = make_auth_client(admin_user, institution)
        payload = {
            "full_name": "Ana Rodrigues",
            "student_code": "EST-9999",
            "email": "ana@school.ao",
        }
        resp = client.post(self.URL, payload)
        assert resp.status_code == 201
        assert resp.json()["student_code"] == "EST-9999"
        assert "temp_password" in resp.json()

    def test_admin_can_create_student_without_email(self, db, institution, admin_user):
        client = make_auth_client(admin_user, institution)
        resp = client.post(self.URL, {"full_name": "Sem Email"})
        assert resp.status_code == 201
        assert "temp_password" not in resp.json()

    def test_trainer_cannot_create_student(self, db, institution, trainer_user):
        client = make_auth_client(trainer_user, institution)
        resp = client.post(self.URL, {"full_name": "X", "student_code": "X-001"})
        assert resp.status_code == 403


@pytest.mark.django_db
class TestStudentDetailView:

    def _url(self, student_id):
        return f"/api/students/{student_id}/"

    def test_admin_get_detail(self, db, institution, admin_user, student):
        client = make_auth_client(admin_user, institution)
        resp = client.get(self._url(student.id))
        assert resp.status_code == 200
        assert resp.json()["id"] == str(student.id)

    def test_trainer_get_detail(self, db, institution, trainer_user, student):
        client = make_auth_client(trainer_user, institution)
        resp = client.get(self._url(student.id))
        assert resp.status_code == 200

    def test_student_cannot_get_detail(self, db, institution, student_user, student):
        client = make_auth_client(student_user, institution)
        resp = client.get(self._url(student.id))
        assert resp.status_code == 403

    def test_admin_patch(self, db, institution, admin_user, student):
        client = make_auth_client(admin_user, institution)
        resp = client.patch(
            self._url(student.id), {"full_name": "New Name"},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "New Name"

    def test_trainer_cannot_patch(self, db, institution, trainer_user, student):
        client = make_auth_client(trainer_user, institution)
        resp = client.patch(
            self._url(student.id), {"full_name": "Hack"},
            format='json',
        )
        assert resp.status_code == 403

    def test_admin_delete(self, db, institution, admin_user, student):
        client = make_auth_client(admin_user, institution)
        resp = client.delete(self._url(student.id))
        assert resp.status_code == 204

    def test_cannot_access_other_institution_student(self, db, institution, admin_user):
        other_student = StudentFactory(institution=InstitutionFactory())
        client = make_auth_client(admin_user, institution)
        resp = client.get(self._url(other_student.id))
        assert resp.status_code == 404

    def test_get_returns_404_for_nonexistent(self, db, institution, admin_user):
        import uuid
        client = make_auth_client(admin_user, institution)
        resp = client.get(self._url(uuid.uuid4()))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestMyStudentProfileView:

    URL = "/api/students/me/"

    def test_student_sees_own_profile(self, db, institution):
        user = UserFactory()
        MembershipFactory(user=user, institution=institution, role="student")
        student = StudentFactory(institution=institution, user=user)
        client = make_auth_client(user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert resp.json()["id"] == str(student.id)

    def test_user_without_student_profile_returns_404(self, db, institution, student_user):
        # student_user has membership but no Student record linked
        client = make_auth_client(student_user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 404


@pytest.mark.django_db
class TestStudentResetPasswordView:

    def _url(self, student_id):
        return f"/api/students/{student_id}/reset-password/"

    def test_admin_can_reset_password(self, db, institution, admin_user):
        user = UserFactory()
        MembershipFactory(user=user, institution=institution, role="student")
        student = StudentFactory(institution=institution, user=user)
        client = make_auth_client(admin_user, institution)
        resp = client.post(self._url(student.id))
        assert resp.status_code == 200
        assert "temp_password" in resp.json()
        user.refresh_from_db()
        assert user.must_change_password is True
        assert user.check_password(resp.json()["temp_password"])

    def test_student_without_user_returns_400(self, db, institution, admin_user, student):
        client = make_auth_client(admin_user, institution)
        resp = client.post(self._url(student.id))
        assert resp.status_code == 400

    def test_trainer_cannot_reset_password(self, db, institution, trainer_user, student):
        client = make_auth_client(trainer_user, institution)
        resp = client.post(self._url(student.id))
        assert resp.status_code == 403

    def test_cannot_reset_password_for_other_institution(self, db, institution, admin_user):
        other_student = StudentFactory(institution=InstitutionFactory())
        client = make_auth_client(admin_user, institution)
        resp = client.post(self._url(other_student.id))
        assert resp.status_code == 404
