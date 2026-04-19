"""
Tests for UserService and MembershipService.
User is a global identity. Role and institution context lives in Membership.
"""

import pytest
from rest_framework.exceptions import ValidationError, NotFound

from apps.accounts.services import UserService, MembershipService
from conftest import InstitutionFactory, UserFactory, MembershipFactory


@pytest.mark.django_db
class TestUserServiceCreate:

    def test_create_user_success(self, db):
        user = UserService.create_user(
            email="novo@academico.ao",
            password="senha123",
            full_name="Ana Ferreira",
        )
        assert user.email == "novo@academico.ao"
        assert user.full_name == "Ana Ferreira"
        assert user.check_password("senha123")

    def test_create_user_normalises_email_domain_only(self, db):
        user = UserService.create_user(email="NOVO@ACADEMICO.AO", password="senha123")
        # Django normalize_email only lowercases the domain
        assert user.email == "NOVO@academico.ao"

    def test_create_user_duplicate_email_raises(self, db):
        UserService.create_user(email="dup@academico.ao", password="senha123")
        with pytest.raises(ValidationError) as exc:
            UserService.create_user(email="dup@academico.ao", password="outra")
        assert "email" in exc.value.detail

    def test_same_user_memberships_at_multiple_institutions(self, db):
        """A single user can have memberships at different institutions."""
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        user = UserService.create_user(email="shared@academico.ao", password="senha123")
        MembershipService.create_membership(user, inst_a, "student")
        MembershipService.create_membership(user, inst_b, "trainer")
        assert user.memberships.count() == 2


@pytest.mark.django_db
class TestUserServiceGet:

    def test_get_user_by_id(self, db):
        user = UserFactory()
        found = UserService.get_user(str(user.id))
        assert found.id == user.id

    def test_get_user_not_found(self, db):
        import uuid

        with pytest.raises(NotFound):
            UserService.get_user(str(uuid.uuid4()))

    def test_get_user_by_email(self, db):
        UserFactory(email="find@academico.ao")
        found = UserService.get_user_by_email("find@academico.ao")
        assert found.email == "find@academico.ao"

    def test_get_user_by_email_not_found(self, db):
        with pytest.raises(NotFound):
            UserService.get_user_by_email("naoexiste@academico.ao")


@pytest.mark.django_db
class TestUserServiceUpdate:

    def test_update_full_name(self, db):
        user = UserFactory()
        updated = UserService.update_user(user, {"full_name": "Novo Nome"})
        assert updated.full_name == "Novo Nome"

    def test_update_ignores_disallowed_fields(self, db):
        user = UserFactory(email="original@academico.ao")
        UserService.update_user(user, {"email": "hacked@academico.ao"})
        user.refresh_from_db()
        assert user.email == "original@academico.ao"

    def test_deactivate_user(self, db):
        user = UserFactory()
        UserService.deactivate_user(user)
        user.refresh_from_db()
        assert user.is_active is False


@pytest.mark.django_db
class TestUserServicePassword:

    def test_change_password_success(self, db):
        user = UserFactory()
        UserService.change_password(user, "testpass123", "novasenha456")
        user.refresh_from_db()
        assert user.check_password("novasenha456")

    def test_change_password_wrong_old_raises(self, db):
        user = UserFactory()
        with pytest.raises(ValidationError) as exc:
            UserService.change_password(user, "errada", "novasenha")
        assert "old_password" in exc.value.detail


@pytest.mark.django_db
class TestMembershipServiceCreate:

    def test_create_membership_success(self, institution):
        user = UserFactory()
        m = MembershipService.create_membership(user, institution, "admin")
        assert m.role == "admin"
        assert m.institution == institution
        assert m.user == user
        assert m.is_active is True

    def test_create_membership_invalid_role_raises(self, institution):
        user = UserFactory()
        with pytest.raises(ValidationError) as exc:
            MembershipService.create_membership(user, institution, "superadmin")
        assert "role" in exc.value.detail

    def test_create_duplicate_exact_membership_raises(self, institution):
        user = UserFactory()
        MembershipService.create_membership(user, institution, "student")
        with pytest.raises(ValidationError) as exc:
            MembershipService.create_membership(user, institution, "student")
        assert "membership" in exc.value.detail

    def test_same_user_different_roles_same_institution(self, institution):
        """A user can have both student and trainer roles at the same institution."""
        user = UserFactory()
        MembershipService.create_membership(user, institution, "student")
        m2 = MembershipService.create_membership(user, institution, "trainer")
        assert m2.role == "trainer"
        assert user.memberships.filter(institution=institution).count() == 2

    def test_same_user_multiple_institutions(self, db):
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        user = UserFactory()
        MembershipService.create_membership(user, inst_a, "student")
        MembershipService.create_membership(user, inst_b, "admin")
        assert user.memberships.count() == 2


@pytest.mark.django_db
class TestMembershipServiceList:

    def test_list_scoped_to_institution(self, db):
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        u1 = UserFactory()
        u2 = UserFactory()
        MembershipFactory(user=u1, institution=inst_a, role="admin")
        MembershipFactory(user=u2, institution=inst_b, role="student")
        result = list(MembershipService.list_memberships(inst_a))
        assert len(result) == 1
        assert result[0].user == u1

    def test_list_filter_by_role(self, institution):
        u1 = UserFactory()
        u2 = UserFactory()
        MembershipFactory(user=u1, institution=institution, role="admin")
        MembershipFactory(user=u2, institution=institution, role="student")
        result = list(MembershipService.list_memberships(institution, role="admin"))
        assert all(m.role == "admin" for m in result)

    def test_list_filter_by_active(self, institution):
        user = UserFactory()
        m = MembershipFactory(user=user, institution=institution, role="student")
        MembershipService.deactivate_membership(m)
        active = list(MembershipService.list_memberships(institution, is_active=True))
        assert all(m.is_active for m in active)


@pytest.mark.django_db
class TestMembershipServiceDeactivate:

    def test_deactivate_membership(self, institution):
        user = UserFactory()
        m = MembershipFactory(user=user, institution=institution, role="student")
        MembershipService.deactivate_membership(m)
        m.refresh_from_db()
        assert m.is_active is False

    def test_revoke_all_memberships(self, db):
        inst = InstitutionFactory()
        user = UserFactory()
        MembershipFactory(user=user, institution=inst, role="student")
        MembershipFactory(user=user, institution=inst, role="trainer")
        count = MembershipService.revoke_all_memberships(user, inst)
        assert count == 2
        assert user.memberships.filter(institution=inst, is_active=True).count() == 0
