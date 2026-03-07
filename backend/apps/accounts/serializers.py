from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default JWT serializer to include
    role and institution_id in both the token payload
    and the login response body.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["institution_id"] = (
            str(user.institution_id) if user.institution_id else None
        )
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserMeSerializer(self.user).data
        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "email", "role", "is_active", "institution", "created_at"]
        read_only_fields = ["id", "created_at", "institution"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "password", "role"]

    def validate_role(self, value):
        valid = [r.value for r in User.Role]
        if value not in valid:
            raise serializers.ValidationError(f"Must be one of: {valid}")
        return value


class UserMeSerializer(serializers.ModelSerializer):
    institution_id = serializers.UUIDField(source="institution.id", read_only=True)
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "institution_id",
            "institution_name",
            "created_at",
        ]
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
