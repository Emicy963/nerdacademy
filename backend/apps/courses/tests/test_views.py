"""
HTTP-layer tests for courses endpoints.
"""

import pytest
from conftest import InstitutionFactory, CourseFactory, make_auth_client


@pytest.mark.django_db
class TestCourseListCreateView:

    URL = "/api/courses/"

    def test_unauthenticated_returns_401(self, client):
        assert client.get(self.URL).status_code == 401

    def test_all_roles_can_list(self, db, institution, admin_user, trainer_user, student_user):
        CourseFactory.create_batch(3, institution=institution)
        for user in (admin_user, trainer_user, student_user):
            resp = make_auth_client(user, institution).get(self.URL)
            assert resp.status_code == 200

    def test_list_scoped_to_institution(self, db, institution, admin_user):
        CourseFactory.create_batch(2, institution=institution)
        CourseFactory.create_batch(5, institution=InstitutionFactory())
        resp = make_auth_client(admin_user, institution).get(self.URL)
        assert resp.json()["count"] == 2

    def test_admin_can_create(self, db, institution, admin_user):
        resp = make_auth_client(admin_user, institution).post(self.URL, {
            "name": "Redes Informáticas",
            "code": "NET-2025",
            "total_hours": 120,
        })
        assert resp.status_code == 201
        assert resp.json()["code"] == "NET-2025"

    def test_trainer_cannot_create(self, db, institution, trainer_user):
        resp = make_auth_client(trainer_user, institution).post(self.URL, {
            "name": "X", "code": "X-001",
        })
        assert resp.status_code == 403

    def test_student_cannot_create(self, db, institution, student_user):
        resp = make_auth_client(student_user, institution).post(self.URL, {
            "name": "X", "code": "X-001",
        })
        assert resp.status_code == 403

    def test_duplicate_code_same_institution_returns_400(self, db, institution, admin_user):
        CourseFactory(institution=institution, code="DUP-001", name="Original")
        resp = make_auth_client(admin_user, institution).post(self.URL, {
            "name": "Duplicate", "code": "DUP-001",
        })
        assert resp.status_code == 400


@pytest.mark.django_db
class TestCourseDetailView:

    def _url(self, course_id):
        return f"/api/courses/{course_id}/"

    def test_all_roles_can_get(self, db, institution, admin_user, trainer_user, student_user, course):
        for user in (admin_user, trainer_user, student_user):
            resp = make_auth_client(user, institution).get(self._url(course.id))
            assert resp.status_code == 200

    def test_admin_patch(self, db, institution, admin_user, course):
        resp = make_auth_client(admin_user, institution).patch(
            self._url(course.id), {"name": "Updated"},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"

    def test_trainer_cannot_patch(self, db, institution, trainer_user, course):
        resp = make_auth_client(trainer_user, institution).patch(
            self._url(course.id), {"name": "Hack"},
            format='json',
        )
        assert resp.status_code == 403

    def test_admin_delete(self, db, institution, admin_user, course):
        resp = make_auth_client(admin_user, institution).delete(self._url(course.id))
        assert resp.status_code == 204

    def test_cannot_access_other_institution_course(self, db, institution, admin_user):
        other_course = CourseFactory(institution=InstitutionFactory())
        resp = make_auth_client(admin_user, institution).get(self._url(other_course.id))
        assert resp.status_code == 404
