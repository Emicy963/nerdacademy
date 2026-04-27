"""
Tests for CourseService: CRUD, code uniqueness, search, deactivation.
"""

import pytest
from rest_framework.exceptions import ValidationError, NotFound

from apps.courses.services import CourseService
from conftest import InstitutionFactory, CourseFactory


@pytest.mark.django_db
class TestCourseServiceCreate:

    def test_create_course_success(self, institution):
        course = CourseService.create_course(
            institution=institution,
            name="Desenvolvimento Web",
            code="WD-2024",
            total_hours=240,
        )
        assert course.name == "Desenvolvimento Web"
        assert course.code == "WD-2024"
        assert course.is_active is True

    def test_create_course_normalises_code_to_uppercase(self, institution):
        course = CourseService.create_course(
            institution=institution,
            name="Python",
            code="py-2024",
        )
        assert course.code == "PY-2024"

    def test_create_course_duplicate_code_same_institution(self, institution):
        CourseFactory(institution=institution, code="DUP-001")
        with pytest.raises(ValidationError) as exc:
            CourseService.create_course(
                institution=institution,
                name="Outro Curso",
                code="DUP-001",
            )
        assert "code" in exc.value.detail

    def test_create_course_same_code_different_institution(self, db):
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        CourseFactory(institution=inst_a, code="SHARED-001")
        c = CourseService.create_course(
            institution=inst_b,
            name="Curso B",
            code="SHARED-001",
        )
        assert c.institution == inst_b


@pytest.mark.django_db
class TestCourseServiceGet:

    def test_get_course_success(self, institution, course):
        found = CourseService.get_course(str(course.id), institution)
        assert found.id == course.id

    def test_get_course_wrong_institution(self, course):
        other = InstitutionFactory()
        with pytest.raises(NotFound):
            CourseService.get_course(str(course.id), other)

    def test_get_course_not_found(self, institution):
        import uuid

        with pytest.raises(NotFound):
            CourseService.get_course(str(uuid.uuid4()), institution)


@pytest.mark.django_db
class TestCourseServiceUpdate:

    def test_update_name_and_hours(self, institution, course):
        updated = CourseService.update_course(
            course, {"name": "Novo Nome", "total_hours": 300}
        )
        assert updated.name == "Novo Nome"
        assert updated.total_hours == 300

    def test_update_ignores_code(self, institution, course):
        original_code = course.code
        CourseService.update_course(course, {"code": "HACK-999"})
        course.refresh_from_db()
        assert course.code == original_code

    def test_deactivate_course(self, institution, course):
        CourseService.deactivate_course(course)
        course.refresh_from_db()
        assert course.is_active is False


@pytest.mark.django_db
class TestCourseServiceList:

    def test_list_scoped_to_institution(self, db):
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        CourseFactory.create_batch(3, institution=inst_a)
        CourseFactory(institution=inst_b)
        result = list(CourseService.list_courses(inst_a))
        assert len(result) == 3

    def test_list_search_by_name(self, institution):
        CourseFactory(institution=institution, name="Redes Informáticas")
        CourseFactory(institution=institution, name="Base de Dados")
        result = list(CourseService.list_courses(institution, search="redes"))
        assert len(result) == 1

    def test_list_search_by_code(self, institution):
        CourseFactory(institution=institution, code="NET-001", name="Redes Informáticas")
        CourseFactory(institution=institution, code="DB-001", name="Base de Dados")
        result = list(CourseService.list_courses(institution, search="NET"))
        assert len(result) == 1

    def test_list_filter_active_only(self, institution):
        c = CourseFactory(institution=institution)
        CourseService.deactivate_course(c)
        result = list(CourseService.list_courses(institution, is_active=True))
        assert all(c.is_active for c in result)

    def test_list_ordered_by_name(self, institution):
        CourseFactory(institution=institution, name="Zebra")
        CourseFactory(institution=institution, name="Alpha")
        names = [c.name for c in CourseService.list_courses(institution)]
        assert names == sorted(names)
