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
