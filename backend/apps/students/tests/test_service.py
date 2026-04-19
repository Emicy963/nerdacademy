"""
Tests for StudentService: CRUD, search, deactivation, user linking.
"""

import pytest
from rest_framework.exceptions import ValidationError, NotFound

from apps.students.services import StudentService
from conftest import InstitutionFactory, StudentFactory, StudentUserFactory


@pytest.mark.django_db
class TestStudentServiceCreate:

    def test_create_student_success(self, institution):
        student = StudentService.create_student(
            institution=institution,
            full_name="Ana Luísa Ferreira",
            student_code="EST-001",
        )
        assert student.full_name == "Ana Luísa Ferreira"
        assert student.student_code == "EST-001"
        assert student.institution == institution
        assert student.is_active is True

    def test_create_student_duplicate_code_same_institution(self, institution):
        StudentFactory(institution=institution, student_code="EST-001")
        with pytest.raises(ValidationError) as exc:
            StudentService.create_student(
                institution=institution,
                full_name="Outro Aluno",
                student_code="EST-001",
            )
        assert "student_code" in exc.value.detail

    def test_create_student_same_code_different_institution(self, db):
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        StudentFactory(institution=inst_a, student_code="EST-001")
        # Should succeed — different institution
        s = StudentService.create_student(
            institution=inst_b,
            full_name="Outro",
            student_code="EST-001",
        )
        assert s.institution == inst_b


@pytest.mark.django_db
class TestStudentServiceGet:

    def test_get_student_success(self, institution, student):
        found = StudentService.get_student(str(student.id), institution)
        assert found.id == student.id

    def test_get_student_wrong_institution(self, student):
        other = InstitutionFactory()
        with pytest.raises(NotFound):
            StudentService.get_student(str(student.id), other)

    def test_get_student_not_found(self, institution):
        import uuid

        with pytest.raises(NotFound):
            StudentService.get_student(str(uuid.uuid4()), institution)


@pytest.mark.django_db
class TestStudentServiceUpdate:

    def test_update_allowed_fields(self, institution, student):
        updated = StudentService.update_student(
            student, {"full_name": "Nome Actualizado", "phone": "+244 900 000 001"}
        )
        assert updated.full_name == "Nome Actualizado"
        assert updated.phone == "+244 900 000 001"

    def test_update_ignores_student_code(self, institution, student):
        original_code = student.student_code
        StudentService.update_student(student, {"student_code": "HACK-999"})
        student.refresh_from_db()
        assert student.student_code == original_code

    def test_deactivate_student(self, institution, student):
        assert student.is_active is True
        StudentService.deactivate_student(student)
        student.refresh_from_db()
        assert student.is_active is False


@pytest.mark.django_db
class TestStudentServiceList:

    def test_list_scoped_to_institution(self, db):
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        StudentFactory.create_batch(3, institution=inst_a)
        StudentFactory.create_batch(2, institution=inst_b)
        result = list(StudentService.list_students(inst_a))
        assert len(result) == 3
        assert all(s.institution_id == inst_a.id for s in result)

    def test_list_search_by_name(self, institution):
        StudentFactory(institution=institution, full_name="Carlos Mendes")
        StudentFactory(institution=institution, full_name="Ana Silva")
        result = list(StudentService.list_students(institution, search="carlos"))
        assert len(result) == 1
        assert result[0].full_name == "Carlos Mendes"

    def test_list_search_by_code(self, institution):
        StudentFactory(institution=institution, student_code="EST-999")
        StudentFactory(institution=institution, student_code="EST-001")
        result = list(StudentService.list_students(institution, search="999"))
        assert len(result) == 1
        assert result[0].student_code == "EST-999"

    def test_list_filter_active(self, institution):
        StudentFactory(institution=institution, is_active=True)
        s = StudentFactory(institution=institution, is_active=True)
        StudentService.deactivate_student(s)
        result = list(StudentService.list_students(institution, is_active=True))
        assert all(s.is_active for s in result)

    def test_list_filter_inactive(self, institution):
        s = StudentFactory(institution=institution)
        StudentService.deactivate_student(s)
        result = list(StudentService.list_students(institution, is_active=False))
        assert all(not s.is_active for s in result)


@pytest.mark.django_db
class TestStudentServiceLinkUser:

    def test_link_user_success(self, institution, student):
        user = StudentUserFactory(institution=institution)
        linked = StudentService.link_user(student, user)
        assert linked.user == user

    def test_link_user_wrong_institution(self, institution, student):
        other = InstitutionFactory()
        user = StudentUserFactory(institution=other)
        with pytest.raises(ValidationError) as exc:
            StudentService.link_user(student, user)
        assert "user" in exc.value.detail

    def test_link_user_wrong_role(self, institution, student):
        from conftest import TrainerUserFactory

        user = TrainerUserFactory(institution=institution)
        with pytest.raises(ValidationError) as exc:
            StudentService.link_user(student, user)
        assert "user" in exc.value.detail

    def test_link_user_already_linked(self, institution):
        s1 = StudentFactory(institution=institution)
        s2 = StudentFactory(institution=institution)
        user = StudentUserFactory(institution=institution)
        StudentService.link_user(s1, user)
        with pytest.raises(ValidationError) as exc:
            StudentService.link_user(s2, user)
        assert "user" in exc.value.detail
