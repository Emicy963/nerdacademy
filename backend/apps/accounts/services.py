from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, NotFound

User = get_user_model()


class UserService:

    @staticmethod
    def create_user(institution, email: str, password: str, role: str) -> User:
        """
        Create a user bound to an institution.
        Validates role and email uniqueness within the institution.
        """
        valid_roles = [r.value for r in User.Role]
        if role not in valid_roles:
            raise ValidationError({"role": f"Must be one of: {valid_roles}"})

        email = User.objects.normalize_email(email)

        if User.objects.filter(institution=institution, email=email).exists():
            raise ValidationError(
                {"email": "A user with this email already exists in this institution."}
            )

        user = User.objects.create_user(
            email=email,
            password=password,
            institution=institution,
            role=role,
        )
        return user

    @staticmethod
    def get_user(user_id: str, institution) -> User:
        try:
            return User.objects.select_related("institution").get(
                id=user_id,
                institution=institution,
            )
        except User.DoesNotExist:
            raise NotFound("User not found.")

    @staticmethod
    def update_user(user: User, data: dict) -> User:
        """
        Update allowed user fields.
        Password changes must go through change_password().
        """
        allowed = {"email", "role", "is_active"}
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

    @staticmethod
    def list_users(institution, role: str = None, is_active: bool = None):
        qs = User.objects.select_related("institution").filter(institution=institution)
        if role:
            qs = qs.filter(role=role)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs.order_by("email")
