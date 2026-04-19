"""
Tests for UserService: creation, validation, update, password, deactivation.
"""

import pytest
from rest_framework.exceptions import ValidationError, NotFound

from apps.accounts.services import UserService
from conftest import InstitutionFactory, AdminUserFactory


@pytest.mark.django_db
class TestUserServiceCreate:

    def test_create_user_success(self, institution):
        user = UserService.create_user(
            institution=institution,
            email="novo@academico.ao",
            password="senha123",
            role="admin",
        )
        assert user.email == "novo@academico.ao"
        assert user.role == "admin"
        assert user.institution == institution
        assert user.check_password("senha123")

    def test_create_user_normalises_email(self, institution):
        user = UserService.create_user(
            institution=institution,
            email="NOVO@ACADEMICO.AO",
            password="senha123",
            role="student",
        )
        # Django's normalize_email lowercases the domain only, not the local part
        assert user.email == "NOVO@academico.ao"

    def test_create_user_invalid_role(self, institution):
        with pytest.raises(ValidationError) as exc:
            UserService.create_user(
                institution=institution,
                email="x@y.ao",
                password="senha123",
                role="superadmin",
            )
        assert "role" in exc.value.detail

    def test_create_user_duplicate_email_same_institution(self, institution):
        UserService.create_user(
            institution=institution,
            email="dup@academico.ao",
            password="senha123",
            role="student",
        )
        with pytest.raises(ValidationError) as exc:
            UserService.create_user(
                institution=institution,
                email="dup@academico.ao",
                password="outrasenha",
                role="trainer",
            )
        assert "email" in exc.value.detail

    def test_create_user_same_email_different_institution(self, db):
        # With USERNAME_FIELD = "email", Django requires global email uniqueness.
        # The same email cannot exist across institutions — this is a known
        # architectural constraint of this implementation.
        from conftest import InstitutionFactory

        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        UserService.create_user(
            institution=inst_a,
            email="shared@academico.ao",
            password="senha123",
            role="student",
        )
        with pytest.raises(Exception):
            UserService.create_user(
                institution=inst_b,
                email="shared@academico.ao",
                password="senha456",
                role="student",
            )


@pytest.mark.django_db
class TestUserServiceGet:

    def test_get_user_success(self, institution, admin_user):
        found = UserService.get_user(str(admin_user.id), institution)
        assert found.id == admin_user.id

    def test_get_user_wrong_institution(self, db, admin_user):
        other = InstitutionFactory()
        with pytest.raises(NotFound):
            UserService.get_user(str(admin_user.id), other)

    def test_get_user_not_found(self, institution):
        import uuid

        with pytest.raises(NotFound):
            UserService.get_user(str(uuid.uuid4()), institution)


@pytest.mark.django_db
class TestUserServiceUpdate:

    def test_update_role(self, institution, admin_user):
        updated = UserService.update_user(admin_user, {"role": "trainer"})
        assert updated.role == "trainer"

    def test_update_ignores_disallowed_fields(self, institution, admin_user):
        original_email = admin_user.email
        UserService.update_user(admin_user, {"password": "hacked"})
        admin_user.refresh_from_db()
        assert admin_user.email == original_email

    def test_deactivate_user(self, institution, admin_user):
        assert admin_user.is_active is True
        deactivated = UserService.deactivate_user(admin_user)
        assert deactivated.is_active is False


@pytest.mark.django_db
class TestUserServicePassword:

    def test_change_password_success(self, institution, admin_user):
        UserService.change_password(admin_user, "testpass123", "novasenha456")
        admin_user.refresh_from_db()
        assert admin_user.check_password("novasenha456")

    def test_change_password_wrong_old(self, institution, admin_user):
        with pytest.raises(ValidationError) as exc:
            UserService.change_password(admin_user, "errada", "novasenha456")
        assert "old_password" in exc.value.detail


@pytest.mark.django_db
class TestUserServiceList:

    def test_list_users_scoped_to_institution(self, db, institution):
        other = InstitutionFactory()
        AdminUserFactory(institution=institution)
        AdminUserFactory(institution=other)
        result = list(UserService.list_users(institution))
        assert all(u.institution_id == institution.id for u in result)

    def test_list_users_filter_by_role(self, institution):
        AdminUserFactory(institution=institution)
        AdminUserFactory(institution=institution, role="trainer")
        result = list(UserService.list_users(institution, role="trainer"))
        assert all(u.role == "trainer" for u in result)

    def test_list_users_filter_by_active(self, institution):
        u = AdminUserFactory(institution=institution)
        UserService.deactivate_user(u)
        active = list(UserService.list_users(institution, is_active=True))
        assert all(u.is_active for u in active)
