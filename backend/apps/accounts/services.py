from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError, NotFound

from .models import Membership

User = get_user_model()


class UserService:

    @staticmethod
    def create_user(
        email: str, password: str, full_name: str = "", must_change_password: bool = False
    ) -> User:
        """
        Create a global user identity.
        Does not assign any institution or role — use MembershipService for that.
        """
        email = User.objects.normalize_email(email)
        if User.objects.filter(email=email).exists():
            raise ValidationError({"email": "A user with this email already exists."})
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
        )
        if must_change_password:
            user.must_change_password = True
            user.save(update_fields=["must_change_password"])
        return user

    @staticmethod
    def create_managed_user(
        email: str, full_name: str, institution, role: str, code: str = ""
    ):
        """
        Creates a user with must_change_password=True and a membership at the institution.
        - With email: random secure password; caller is responsible for sending welcome email.
        - Without email: placeholder address derived from code, fixed password 'pass123'.
        Returns (user, plain_password).
        """
        import secrets

        if email:
            password = secrets.token_urlsafe(8)
            user_email = email
        else:
            password = secrets.token_urlsafe(8)
            user_email = f"{code.lower()}@local.academico"

        user = UserService.create_user(
            email=user_email,
            password=password,
            full_name=full_name,
            must_change_password=True,
        )
        MembershipService.create_membership(user=user, institution=institution, role=role)
        return user, password

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
    def update_me(user: User, email: str) -> User:
        email = User.objects.normalize_email(email)
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            raise ValidationError({"email": "A user with this email already exists."})
        user.email = email
        user.save(update_fields=["email"])
        return user

    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> User:
        if not user.check_password(old_password):
            raise ValidationError({"old_password": "Incorrect password."})
        try:
            django_validate_password(new_password, user)
        except DjangoValidationError as e:
            raise ValidationError({"new_password": list(e.messages)})
        user.set_password(new_password)
        user.save()
        return user

    @staticmethod
    def reset_password(user: User) -> str:
        """Generate a new temp password and force must_change_password on next login."""
        import secrets

        password = secrets.token_urlsafe(8)
        user.set_password(password)
        user.must_change_password = True
        user.save(update_fields=["password", "must_change_password"])
        from apps.accounts.emails import send_password_reset
        send_password_reset(user, password)
        return password

    @staticmethod
    def request_password_reset(email: str) -> None:
        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.conf import settings

        try:
            user = UserService.get_user_by_email(email)
        except Exception:
            return  # silent — never reveal whether the email exists

        if user.email.endswith("@local.academico") or not user.is_active:
            return  # placeholder or deactivated — silently skip

        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = (
            f"{settings.FRONTEND_URL}/pages/reset-password.html"
            f"#{uid}:{token}"
        )

        from apps.accounts.emails import send_password_reset_link
        send_password_reset_link(user, reset_url)

    @staticmethod
    def confirm_password_reset(uid_b64: str, token: str, new_password: str) -> None:
        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_str

        try:
            uid = force_str(urlsafe_base64_decode(uid_b64))
            user = User.objects.get(pk=uid)
        except Exception:
            raise ValidationError({"token": "Link inválido ou expirado."})

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise ValidationError({"token": "Link inválido ou expirado."})

        try:
            django_validate_password(new_password, user)
        except DjangoValidationError as e:
            raise ValidationError({"new_password": list(e.messages)})
        user.set_password(new_password)
        user.must_change_password = False
        user.save(update_fields=["password", "must_change_password"])

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
