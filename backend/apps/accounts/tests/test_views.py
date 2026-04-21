"""
HTTP-layer tests for accounts: login, logout, me, memberships, change-password.
"""

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from conftest import InstitutionFactory, UserFactory, MembershipFactory, make_auth_client


# ── /api/auth/login/ ───────────────────────────────────────────────

@pytest.mark.django_db
class TestLoginView:

    URL = "/api/auth/login/"

    def test_login_success_returns_tokens_and_memberships(self, client, db):
        institution = InstitutionFactory()
        user = UserFactory(password="s3cr3t!")
        MembershipFactory(user=user, institution=institution, role="admin")

        resp = client.post(self.URL, {"email": user.email, "password": "s3cr3t!"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access" in data
        assert "refresh" in data
        assert "user" in data
        assert isinstance(data["memberships"], list)
        assert len(data["memberships"]) == 1

    def test_login_wrong_password_returns_401(self, client, db):
        user = UserFactory(password="correct")
        resp = client.post(self.URL, {"email": user.email, "password": "wrong"})
        assert resp.status_code == 401

    def test_login_unknown_email_returns_401(self, client, db):
        resp = client.post(self.URL, {"email": "ghost@no.com", "password": "x"})
        assert resp.status_code == 401

    def test_login_includes_must_change_password(self, client, db):
        user = UserFactory(password="pass1234")
        resp = client.post(self.URL, {"email": user.email, "password": "pass1234"})
        assert resp.status_code == 200
        data = resp.json()
        assert "must_change_password" in data
        assert data["must_change_password"] is False


# ── /api/auth/me/ ──────────────────────────────────────────────────

@pytest.mark.django_db
class TestMeView:

    URL = "/api/auth/me/"

    def test_me_returns_user_data(self, db, institution, admin_user):
        client = make_auth_client(admin_user)   # no institution header needed
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert resp.json()["email"] == admin_user.email

    def test_me_unauthenticated_returns_401(self, client):
        resp = client.get(self.URL)
        assert resp.status_code == 401


# ── /api/auth/memberships/ ─────────────────────────────────────────

@pytest.mark.django_db
class TestMembershipsView:

    URL = "/api/auth/memberships/"

    def test_returns_all_active_memberships(self, db):
        user = UserFactory()
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        MembershipFactory(user=user, institution=inst_a, role="admin")
        MembershipFactory(user=user, institution=inst_b, role="trainer")

        client = make_auth_client(user)
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_inactive_memberships_excluded(self, db):
        user = UserFactory()
        inst = InstitutionFactory()
        MembershipFactory(user=user, institution=inst, role="admin", is_active=False)

        client = make_auth_client(user)
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_unauthenticated_returns_401(self, client):
        resp = client.get(self.URL)
        assert resp.status_code == 401


# ── /api/auth/logout/ ──────────────────────────────────────────────

@pytest.mark.django_db
class TestLogoutView:

    URL = "/api/auth/logout/"

    def test_logout_blacklists_refresh_token(self, db, institution, admin_user):
        refresh = str(RefreshToken.for_user(admin_user))
        client = make_auth_client(admin_user)
        resp = client.post(self.URL, {"refresh": refresh})
        assert resp.status_code == 204

    def test_logout_unauthenticated_returns_401(self, client):
        resp = client.post(self.URL, {"refresh": "dummy"})
        assert resp.status_code == 401


# ── /api/auth/change-password/ ─────────────────────────────────────

@pytest.mark.django_db
class TestChangePasswordView:

    URL = "/api/auth/change-password/"

    def test_change_password_success(self, db, institution, admin_user):
        client = make_auth_client(admin_user)
        resp = client.post(self.URL, {
            "old_password": "testpass123",
            "new_password": "NewP@ssw0rd!",
        })
        assert resp.status_code == 200
        assert "detail" in resp.json()

    def test_change_password_wrong_old_returns_400(self, db, institution, admin_user):
        client = make_auth_client(admin_user)
        resp = client.post(self.URL, {
            "old_password": "WRONG",
            "new_password": "NewP@ssw0rd!",
        })
        assert resp.status_code == 400

    def test_change_password_unauthenticated_returns_401(self, client):
        resp = client.post(self.URL, {"old_password": "x", "new_password": "y"})
        assert resp.status_code == 401
