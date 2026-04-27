"""
Tests for email notifications: welcome on creation, password reset.
Uses pytest-django's mailoutbox fixture (locmem backend, auto-cleared per test).
"""

import pytest
from conftest import InstitutionFactory, UserFactory, MembershipFactory, StudentFactory, TrainerFactory
from apps.students.services import StudentService
from apps.trainers.services import TrainerService
from apps.accounts.services import UserService


@pytest.mark.django_db
class TestWelcomeEmailStudent:

    def test_welcome_email_sent_when_email_provided(self, institution, mailoutbox):
        StudentService.create_student(
            institution=institution,
            full_name="Ana Costa",
            email="ana@school.ao",
        )
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == ["ana@school.ao"]
        assert "Ana Costa" in mailoutbox[0].body
        assert institution.name in mailoutbox[0].subject

    def test_welcome_email_contains_temp_password(self, institution, mailoutbox):
        _, temp_password = StudentService.create_student(
            institution=institution,
            full_name="João Silva",
            email="joao@school.ao",
        )
        assert temp_password in mailoutbox[0].body

    def test_no_email_sent_without_email(self, institution, mailoutbox):
        StudentService.create_student(institution=institution, full_name="Sem Email")
        assert len(mailoutbox) == 0


@pytest.mark.django_db
class TestWelcomeEmailTrainer:

    def test_welcome_email_sent_when_email_provided(self, institution, mailoutbox):
        TrainerService.create_trainer(
            institution=institution,
            full_name="Prof. Santos",
            specialization="Python",
            email="santos@school.ao",
        )
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == ["santos@school.ao"]
        assert "Prof. Santos" in mailoutbox[0].body

    def test_welcome_email_contains_temp_password(self, institution, mailoutbox):
        _, temp_password = TrainerService.create_trainer(
            institution=institution,
            full_name="Prof. Costa",
            email="costa@school.ao",
        )
        assert temp_password in mailoutbox[0].body

    def test_no_email_sent_without_email(self, institution, mailoutbox):
        TrainerService.create_trainer(institution=institution, full_name="Sem Email")
        assert len(mailoutbox) == 0


@pytest.mark.django_db
class TestPasswordResetEmail:

    def test_reset_password_sends_email(self, db, mailoutbox):
        user = UserFactory(email="user@school.ao")
        UserService.reset_password(user)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == ["user@school.ao"]

    def test_reset_password_email_contains_new_password(self, db, mailoutbox):
        user = UserFactory(email="user@school.ao")
        new_pwd = UserService.reset_password(user)
        assert new_pwd in mailoutbox[0].body
