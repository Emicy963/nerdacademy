"""
Tests for InstitutionService: creation, slug uniqueness, update, retrieval,
self-service registration.
"""

import pytest
from rest_framework.exceptions import ValidationError, NotFound

from apps.institutions.services import InstitutionService
from conftest import InstitutionFactory


@pytest.mark.django_db
class TestInstitutionServiceCreate:

    def test_create_institution_success(self, db):
        inst = InstitutionService.create_institution(
            name="CINFOTEC Huambo",
            slug="cinfotec-huambo",
            email="info@cinfotec.ao",
        )
        assert inst.name == "CINFOTEC Huambo"
        assert inst.slug == "cinfotec-huambo"
        assert inst.is_active is True

    def test_create_institution_duplicate_slug(self, db):
        InstitutionFactory(slug="slug-repetido")
        with pytest.raises(ValidationError) as exc:
            InstitutionService.create_institution(
                name="Outra Instituição",
                slug="slug-repetido",
            )
        assert "slug" in exc.value.detail

    def test_create_institution_minimal_fields(self, db):
        inst = InstitutionService.create_institution(
            name="Escola Básica",
            slug="escola-basica",
        )
        assert inst.phone == ""
        assert inst.address == ""


@pytest.mark.django_db
class TestInstitutionServiceGet:

    def test_get_institution_success(self, institution):
        found = InstitutionService.get_institution(str(institution.id))
        assert found.id == institution.id

    def test_get_institution_not_found(self, db):
        import uuid

        with pytest.raises(NotFound):
            InstitutionService.get_institution(str(uuid.uuid4()))


@pytest.mark.django_db
class TestInstitutionServiceUpdate:

    def test_update_allowed_fields(self, institution):
        updated = InstitutionService.update_institution(
            institution,
            {"name": "Novo Nome", "phone": "+244 999 000 000"},
        )
        assert updated.name == "Novo Nome"
        assert updated.phone == "+244 999 000 000"

    def test_update_ignores_disallowed_fields(self, institution):
        original_slug = institution.slug
        InstitutionService.update_institution(institution, {"slug": "outro-slug"})
        institution.refresh_from_db()
        assert institution.slug == original_slug

    def test_deactivate_via_update(self, institution):
        updated = InstitutionService.update_institution(
            institution, {"is_active": False}
        )
        assert updated.is_active is False


@pytest.mark.django_db
class TestInstitutionServiceList:

    def test_list_returns_all(self, db):
        InstitutionFactory.create_batch(3)
        result = list(InstitutionService.list_institutions())
        assert len(result) >= 3

    def test_list_ordered_by_name(self, db):
        InstitutionFactory(name="Zulu")
        InstitutionFactory(name="Alpha")
        names = [i.name for i in InstitutionService.list_institutions()]
        assert names == sorted(names)


@pytest.mark.django_db
class TestInstitutionServiceCodeGeneration:

    # ── Prefix derivation ──────────────────────────────────────────

    def test_explicit_prefix_is_used_as_is(self, db):
        inst = InstitutionFactory(institution_prefix="CIN")
        assert InstitutionService.get_prefix(inst) == "CIN"

    def test_prefix_is_uppercased(self, db):
        inst = InstitutionFactory(institution_prefix="cin")
        assert InstitutionService.get_prefix(inst) == "CIN"

    def test_derive_prefix_multi_word(self, db):
        inst = InstitutionFactory(name="Centro de Formação", institution_prefix="")
        assert InstitutionService.get_prefix(inst) == "CDF"

    def test_derive_prefix_single_word(self, db):
        inst = InstitutionFactory(name="Cinfotec", institution_prefix="")
        assert InstitutionService.get_prefix(inst) == "CIN"

    def test_create_institution_derives_prefix_when_blank(self, db):
        inst = InstitutionService.create_institution(
            name="Centro Info Angola",
            slug="cia-test",
        )
        assert inst.institution_prefix == "CIA"

    def test_create_institution_keeps_explicit_prefix(self, db):
        inst = InstitutionService.create_institution(
            name="Centro Info Angola",
            slug="cia-explicit",
            institution_prefix="ZZZ",
        )
        assert inst.institution_prefix == "ZZZ"

    def test_update_institution_prefix(self, institution):
        updated = InstitutionService.update_institution(
            institution, {"institution_prefix": "xyz"}
        )
        assert updated.institution_prefix == "XYZ"

    # ── Student code generation ────────────────────────────────────

    def test_student_code_format(self, db):
        inst = InstitutionFactory(institution_prefix="CIN")
        code = InstitutionService.generate_student_code(inst, year=2026)
        assert code == "CIN20260001"

    def test_student_codes_are_sequential(self, db):
        from apps.students.models import Student

        inst = InstitutionFactory(institution_prefix="CIN")
        Student.objects.create(
            institution=inst, full_name="A", student_code="CIN20260001"
        )
        code = InstitutionService.generate_student_code(inst, year=2026)
        assert code == "CIN20260002"

    def test_student_code_handles_gaps(self, db):
        from apps.students.models import Student

        inst = InstitutionFactory(institution_prefix="CIN")
        Student.objects.create(
            institution=inst, full_name="A", student_code="CIN20260001"
        )
        Student.objects.create(
            institution=inst, full_name="B", student_code="CIN20260002"
        )
        # Delete the first one — gap should be filled
        Student.objects.filter(student_code="CIN20260001").delete()
        code = InstitutionService.generate_student_code(inst, year=2026)
        assert code == "CIN20260001"

    def test_student_codes_scoped_per_institution(self, db):
        inst_a = InstitutionFactory(institution_prefix="AAA")
        inst_b = InstitutionFactory(institution_prefix="AAA")
        code_a = InstitutionService.generate_student_code(inst_a, year=2026)
        code_b = InstitutionService.generate_student_code(inst_b, year=2026)
        assert code_a == code_b == "AAA20260001"

    # ── Trainer code generation ────────────────────────────────────

    def test_trainer_code_format(self, db):
        inst = InstitutionFactory(institution_prefix="CIN")
        code = InstitutionService.generate_trainer_code(inst, year=2026)
        assert code == "CINF20260001"

    def test_trainer_codes_are_sequential(self, db):
        from apps.trainers.models import Trainer

        inst = InstitutionFactory(institution_prefix="CIN")
        Trainer.objects.create(
            institution=inst, full_name="T", trainer_code="CINF20260001"
        )
        code = InstitutionService.generate_trainer_code(inst, year=2026)
        assert code == "CINF20260002"

    def test_trainer_code_independent_from_student_code(self, db):
        inst = InstitutionFactory(institution_prefix="CIN")
        student_code = InstitutionService.generate_student_code(inst, year=2026)
        trainer_code = InstitutionService.generate_trainer_code(inst, year=2026)
        assert student_code == "CIN20260001"
        assert trainer_code == "CINF20260001"


@pytest.mark.django_db
class TestInstitutionServiceRegister:

    def test_register_creates_institution_user_membership(self, db):
        from apps.accounts.models import Membership

        result = InstitutionService.register(
            institution_name="Escola Teste",
            admin_name="Admin Silva",
            email="admin@escola.ao",
            password="strongpass123",
        )

        assert "access" in result
        assert "refresh" in result
        assert result["user"]["full_name"] == "Admin Silva"
        assert result["user"]["email"] == "admin@escola.ao"
        assert result["must_change_password"] is False
        assert len(result["memberships"]) == 1
        assert result["memberships"][0]["role"] == "admin"
        membership = Membership.objects.get(id=result["memberships"][0]["id"])
        assert membership.institution.name == "Escola Teste"

    def test_register_derives_unique_slug_on_collision(self, db):
        from apps.institutions.models import Institution

        InstitutionService.register(
            institution_name="Escola Teste",
            admin_name="Admin A",
            email="a@escola.ao",
            password="strongpass123",
        )
        InstitutionService.register(
            institution_name="Escola Teste",
            admin_name="Admin B",
            email="b@escola.ao",
            password="strongpass123",
        )

        slugs = list(Institution.objects.values_list("slug", flat=True))
        assert len(set(slugs)) == 2

    def test_register_duplicate_email_raises(self, db):
        from rest_framework.exceptions import ValidationError

        InstitutionService.register(
            institution_name="Escola A",
            admin_name="Admin A",
            email="dup@escola.ao",
            password="strongpass123",
        )
        with pytest.raises(ValidationError):
            InstitutionService.register(
                institution_name="Escola B",
                admin_name="Admin B",
                email="dup@escola.ao",
                password="strongpass123",
            )
