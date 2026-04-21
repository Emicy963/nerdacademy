"""
Tests for InstitutionService: creation, slug uniqueness, update, retrieval.
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
