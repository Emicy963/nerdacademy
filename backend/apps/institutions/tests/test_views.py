"""
HTTP-layer tests for institutions: GET/PATCH /api/institutions/me/
"""

import pytest
from conftest import InstitutionFactory, UserFactory, MembershipFactory, make_auth_client


@pytest.mark.django_db
class TestInstitutionDetailView:

    URL = "/api/institutions/me/"

    # ── Auth & permissions ─────────────────────────────────────────

    def test_unauthenticated_returns_401(self, client):
        resp = client.get(self.URL)
        assert resp.status_code == 401

    def test_no_institution_header_returns_403(self, db, institution, admin_user):
        # User is authenticated but membership is None → permission denied (403)
        client = make_auth_client(admin_user)   # no institution header
        resp = client.get(self.URL)
        assert resp.status_code == 403

    def test_trainer_get_returns_403(self, db, institution, trainer_user):
        client = make_auth_client(trainer_user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 403

    def test_student_get_returns_403(self, db, institution, student_user):
        client = make_auth_client(student_user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 403

    # ── Happy paths ────────────────────────────────────────────────

    def test_admin_get_returns_own_institution(self, db, institution, admin_user):
        client = make_auth_client(admin_user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert resp.json()["id"] == str(institution.id)
        assert resp.json()["name"] == institution.name

    def test_admin_patch_updates_institution(self, db, institution, admin_user):
        client = make_auth_client(admin_user, institution)
        resp = client.patch(self.URL, {"name": "Updated Name"}, format='json')
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_admin_cannot_access_another_institution(self, db):
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        user = UserFactory()
        MembershipFactory(user=user, institution=inst_a, role="admin")

        # send inst_b's ID but user only has membership at inst_a → 401
        client = make_auth_client(user, inst_b)
        resp = client.get(self.URL)
        assert resp.status_code == 401
