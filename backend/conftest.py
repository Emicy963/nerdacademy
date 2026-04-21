"""
Shared pytest fixtures and factory-boy factories for all test modules.
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta

import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker("pt_PT")


class InstitutionFactory(DjangoModelFactory):
    class Meta:
        model = "institutions.Institution"

    name = factory.Faker("company", locale="pt_BR")
    slug = factory.Sequence(lambda n: f"institution-{n}")
    email = factory.Faker("company_email")
    phone = factory.Faker("phone_number")
    is_active = True


class UserFactory(DjangoModelFactory):
    class Meta:
        model = "accounts.User"

    email = factory.Sequence(lambda n: f"user{n}@academico.ao")
    full_name = factory.Faker("name")
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "testpass123")
        manager = cls._get_manager(model_class)
        return manager.create_user(password=password, **kwargs)


class MembershipFactory(DjangoModelFactory):
    class Meta:
        model = "accounts.Membership"

    user = factory.SubFactory(UserFactory)
    institution = factory.SubFactory(InstitutionFactory)
    role = "student"
    is_active = True


class AdminMembershipFactory(MembershipFactory):
    role = "admin"


class TrainerMembershipFactory(MembershipFactory):
    role = "trainer"


class StudentMembershipFactory(MembershipFactory):
    role = "student"


class TrainerFactory(DjangoModelFactory):
    class Meta:
        model = "trainers.Trainer"

    institution = factory.SubFactory(InstitutionFactory)
    full_name = factory.Faker("name")
    specialization = factory.Faker("job")
    is_active = True


class StudentFactory(DjangoModelFactory):
    class Meta:
        model = "students.Student"

    institution = factory.SubFactory(InstitutionFactory)
    full_name = factory.Faker("name")
    student_code = factory.Sequence(lambda n: f"EST-{n:04d}")
    is_active = True


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = "courses.Course"

    institution = factory.SubFactory(InstitutionFactory)
    name = factory.Faker("bs")
    code = factory.Sequence(lambda n: f"CRS{n:03d}")
    total_hours = factory.Faker("random_int", min=40, max=300)
    is_active = True


class ClassFactory(DjangoModelFactory):
    class Meta:
        model = "classes.Class"

    institution = factory.SubFactory(InstitutionFactory)
    course = factory.SubFactory(CourseFactory)
    trainer = factory.SubFactory(TrainerFactory)
    name = factory.Sequence(lambda n: f"Turma {n}")
    status = "open"
    start_date = factory.LazyFunction(date.today)
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=90))


class EnrollmentFactory(DjangoModelFactory):
    class Meta:
        model = "classes.Enrollment"

    class_instance = factory.SubFactory(ClassFactory)
    student = factory.SubFactory(StudentFactory)
    status = "active"


class GradeFactory(DjangoModelFactory):
    class Meta:
        model = "grades.Grade"

    institution = factory.SubFactory(InstitutionFactory)
    enrollment = factory.SubFactory(EnrollmentFactory)
    assessment_type = "exam"
    value = Decimal("14.00")
    max_value = Decimal("20.00")
    assessed_at = factory.LazyFunction(date.today)
    notes = ""


# ── API client helpers ─────────────────────────────────────────────


def make_auth_client(user, institution=None):
    """
    Returns an APIClient authenticated as *user*.
    If *institution* is given, the X-Institution-Id header is set so that
    MembershipJWTAuthentication can load request.membership.
    """
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import AccessToken

    client = APIClient()
    token = str(AccessToken.for_user(user))
    credentials = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
    if institution is not None:
        credentials["HTTP_X_INSTITUTION_ID"] = str(institution.id)
    client.credentials(**credentials)
    return client


# ── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def institution(db):
    return InstitutionFactory()


@pytest.fixture
def admin_user(db, institution):
    user = UserFactory()
    MembershipFactory(user=user, institution=institution, role="admin")
    return user


@pytest.fixture
def admin_membership(db, admin_user, institution):
    from apps.accounts.models import Membership

    return Membership.objects.get(user=admin_user, institution=institution)


@pytest.fixture
def trainer_user(db, institution):
    user = UserFactory()
    MembershipFactory(user=user, institution=institution, role="trainer")
    return user


@pytest.fixture
def student_user(db, institution):
    user = UserFactory()
    MembershipFactory(user=user, institution=institution, role="student")
    return user


@pytest.fixture
def trainer(db, institution):
    return TrainerFactory(institution=institution)


@pytest.fixture
def student(db, institution):
    return StudentFactory(institution=institution)


@pytest.fixture
def course(db, institution):
    return CourseFactory(institution=institution)


@pytest.fixture
def class_instance(db, institution, course, trainer):
    course.institution = institution
    course.save()
    trainer.institution = institution
    trainer.save()
    return ClassFactory(
        institution=institution,
        course=course,
        trainer=trainer,
        status="open",
    )


@pytest.fixture
def enrollment(db, class_instance, student):
    student.institution = class_instance.institution
    student.save()
    return EnrollmentFactory(class_instance=class_instance, student=student)


@pytest.fixture
def grade(db, enrollment):
    return GradeFactory(
        institution=enrollment.class_instance.institution,
        enrollment=enrollment,
    )
