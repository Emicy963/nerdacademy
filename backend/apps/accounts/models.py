import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Global identity. Represents a person, not a role or institution.
    One User can have multiple Memberships across different institutions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["email"]

    def __str__(self):
        return self.email

    def get_membership(self, institution):
        return self.memberships.filter(institution=institution, is_active=True).first()

    def get_role(self, institution):
        m = self.get_membership(institution)
        return m.role if m else None


class Membership(models.Model):
    """
    Links a User to an Institution with a specific role.
    A user can be a student at one centre and a trainer at another.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        TRAINER = "trainer", "Trainer"
        STUDENT = "student", "Student"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    institution = models.ForeignKey(
        "institutions.Institution",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "memberships"
        ordering = ["joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "institution", "role"],
                name="unique_user_role_per_institution",
            )
        ]

    def __str__(self):
        return f"{self.user.email} — {self.role} @ {self.institution.name}"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_trainer(self):
        return self.role == self.Role.TRAINER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT
