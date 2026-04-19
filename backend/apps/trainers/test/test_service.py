"""
Tests for TrainerService with multi-institution architecture.
"""

import pytest
from rest_framework.exceptions import ValidationError, NotFound

from apps.trainers.services import TrainerService
from conftest import (
    InstitutionFactory,
    TrainerFactory,
    UserFactory,
    MembershipFactory,
    ClassFactory,
    CourseFactory,
)


@pytest.mark.django_db
class TestTrainerServiceCreate:

    def test_create_trainer_success(self, institution):
        trainer = TrainerService.create_trainer(
            institution=institution,
            full_name="Prof. Carlos",
            specialization="Redes Informáticas",
        )
        assert trainer.full_name == "Prof. Carlos"
        assert trainer.institution == institution
        assert trainer.is_active is True

    def test_create_trainer_minimal(self, institution):
        trainer = TrainerService.create_trainer(
            institution=institution,
            full_name="Formador X",
        )
        assert trainer.bio == ""
        assert trainer.phone == ""


@pytest.mark.django_db
class TestTrainerServiceGet:

    def test_get_trainer_success(self, institution, trainer):
        found = TrainerService.get_trainer(str(trainer.id), institution)
        assert found.id == trainer.id

    def test_get_trainer_wrong_institution(self, trainer):
        other = InstitutionFactory()
        with pytest.raises(NotFound):
            TrainerService.get_trainer(str(trainer.id), other)

    def test_get_trainer_not_found(self, institution):
        import uuid

        with pytest.raises(NotFound):
            TrainerService.get_trainer(str(uuid.uuid4()), institution)


@pytest.mark.django_db
class TestTrainerServiceUpdate:

    def test_update_allowed_fields(self, institution, trainer):
        updated = TrainerService.update_trainer(
            trainer,
            {"full_name": "Prof. Actualizado", "specialization": "Cloud"},
        )
        assert updated.full_name == "Prof. Actualizado"
        assert updated.specialization == "Cloud"

    def test_deactivate_trainer(self, institution, trainer):
        TrainerService.deactivate_trainer(trainer)
        trainer.refresh_from_db()
        assert trainer.is_active is False


@pytest.mark.django_db
class TestTrainerServiceList:

    def test_list_scoped_to_institution(self, db):
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        TrainerFactory.create_batch(2, institution=inst_a)
        TrainerFactory(institution=inst_b)
        result = list(TrainerService.list_trainers(inst_a))
        assert len(result) == 2
        assert all(t.institution_id == inst_a.id for t in result)

    def test_list_search_by_name(self, institution):
        TrainerFactory(institution=institution, full_name="Maria Conceição")
        TrainerFactory(institution=institution, full_name="João Silva")
        result = list(TrainerService.list_trainers(institution, search="maria"))
        assert len(result) == 1

    def test_list_search_by_specialization(self, institution):
        TrainerFactory(institution=institution, specialization="Python")
        TrainerFactory(institution=institution, specialization="Java")
        result = list(TrainerService.list_trainers(institution, search="python"))
        assert len(result) == 1

    def test_list_filter_inactive(self, institution):
        t = TrainerFactory(institution=institution)
        TrainerService.deactivate_trainer(t)
        result = list(TrainerService.list_trainers(institution, is_active=False))
        assert all(not t.is_active for t in result)


@pytest.mark.django_db
class TestTrainerServiceLinkUser:

    def test_link_user_success(self, institution, trainer):
        user = UserFactory()
        membership = MembershipFactory(
            user=user, institution=institution, role="trainer"
        )
        linked = TrainerService.link_user(trainer, user, membership)
        assert linked.user == user

    def test_link_user_wrong_role_raises(self, institution, trainer):
        user = UserFactory()
        membership = MembershipFactory(
            user=user, institution=institution, role="student"
        )
        with pytest.raises(ValidationError) as exc:
            TrainerService.link_user(trainer, user, membership)
        assert "user" in exc.value.detail

    def test_link_user_wrong_institution_raises(self, institution, trainer):
        other = InstitutionFactory()
        user = UserFactory()
        membership = MembershipFactory(user=user, institution=other, role="trainer")
        with pytest.raises(ValidationError) as exc:
            TrainerService.link_user(trainer, user, membership)
        assert "user" in exc.value.detail

    def test_same_user_trainer_at_multiple_institutions(self, db):
        """A user can be a trainer at two different institutions."""
        inst_a = InstitutionFactory()
        inst_b = InstitutionFactory()
        trainer_a = TrainerFactory(institution=inst_a)
        trainer_b = TrainerFactory(institution=inst_b)
        user = UserFactory()
        m_a = MembershipFactory(user=user, institution=inst_a, role="trainer")
        m_b = MembershipFactory(user=user, institution=inst_b, role="trainer")
        TrainerService.link_user(trainer_a, user, m_a)
        TrainerService.link_user(trainer_b, user, m_b)
        assert trainer_a.user == user
        assert trainer_b.user == user


@pytest.mark.django_db
class TestTrainerServiceGetByUser:

    def test_get_trainer_by_user_success(self, institution, trainer):
        user = UserFactory()
        membership = MembershipFactory(
            user=user, institution=institution, role="trainer"
        )
        TrainerService.link_user(trainer, user, membership)
        found = TrainerService.get_trainer_by_user(user, institution)
        assert found.id == trainer.id

    def test_get_trainer_by_user_wrong_institution(self, institution, trainer):
        user = UserFactory()
        membership = MembershipFactory(
            user=user, institution=institution, role="trainer"
        )
        TrainerService.link_user(trainer, user, membership)
        other = InstitutionFactory()
        with pytest.raises(NotFound):
            TrainerService.get_trainer_by_user(user, other)

    def test_get_trainer_by_user_not_found(self, institution):
        user = UserFactory()
        with pytest.raises(NotFound):
            TrainerService.get_trainer_by_user(user, institution)


@pytest.mark.django_db
class TestTrainerServiceClasses:

    def test_get_trainer_classes(self, institution, trainer, course):
        course.institution = institution
        course.save()
        cls = ClassFactory(institution=institution, trainer=trainer, course=course)
        classes = list(TrainerService.get_trainer_classes(trainer))
        assert cls in classes
