from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, NotFound

from .models import Membership

User = get_user_model()


class UserService:

    @staticmethod
    def create_user(email: str, password: str, full_name: str = "") -> User:
        """
        Create a global user identity.
        Does not assign any institution or role — use MembershipService for that.
        """
        email = User.objects.normalize_email(email)
        if User.objects.filter(email=email).exists():
            raise ValidationError({"email": "A user with this email already exists."})
        return User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
        )

    @staticmethod
    def get_user(user_id: str) -> User:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found.")

    @staticmethod
    def get_user_by_email(email: str) -> User:
        try:
            return User.objects.get(email=User.objects.normalize_email(email))
        except User.DoesNotExist:
            raise NotFound("User not found.")

    @staticmethod
    def update_user(user: User, data: dict) -> User:
        allowed = {"full_name", "is_active"}
        for field, value in data.items():
            if field in allowed:
                setattr(user, field, value)
        user.save()
        return user

    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> User:
        if not user.check_password(old_password):
            raise ValidationError({"old_password": "Incorrect password."})
        user.set_password(new_password)
        user.save()
        return user

    @staticmethod
    def deactivate_user(user: User) -> User:
        user.is_active = False
        user.save()
        return user


class MembershipService:

    @staticmethod
    def create_membership(user: User, institution, role: str) -> Membership:
        """
        Grant a user a role at an institution.
        Raises if the exact (user, institution, role) combination already exists.
        """
        valid_roles = [r.value for r in Membership.Role]
        if role not in valid_roles:
            raise ValidationError({"role": f"Must be one of: {valid_roles}"})

        if Membership.objects.filter(
            user=user, institution=institution, role=role
        ).exists():
            raise ValidationError(
                {
                    "membership": f"This user already has the role '{role}' at this institution."
                }
            )

        return Membership.objects.create(
            user=user,
            institution=institution,
            role=role,
        )

    @staticmethod
    def get_membership(membership_id: str, institution) -> Membership:
        try:
            return Membership.objects.select_related("user", "institution").get(
                id=membership_id,
                institution=institution,
            )
        except Membership.DoesNotExist:
            raise NotFound("Membership not found.")

    @staticmethod
    def get_active_membership(user: User, institution) -> Membership:
        m = Membership.objects.filter(
            user=user, institution=institution, is_active=True
        ).first()
        if not m:
            raise NotFound(
                "No active membership found for this user at this institution."
            )
        return m

    @staticmethod
    def list_memberships(institution, role: str = None, is_active: bool = None):
        qs = Membership.objects.select_related("user").filter(institution=institution)
        if role:
            qs = qs.filter(role=role)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs.order_by("user__email")

    @staticmethod
    def deactivate_membership(membership: Membership) -> Membership:
        membership.is_active = False
        membership.save()
        return membership

    @staticmethod
    def revoke_all_memberships(user: User, institution) -> int:
        """Deactivate all memberships a user has at an institution."""
        return Membership.objects.filter(user=user, institution=institution).update(
            is_active=False
        )
