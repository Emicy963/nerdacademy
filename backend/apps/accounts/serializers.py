from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Membership

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        identifier = attrs.get(self.username_field, "")

        # Code-based login: no "@" → look up student or trainer code
        if "@" not in identifier:
            from apps.students.models import Student
            from apps.trainers.models import Trainer

            code = identifier.strip().upper()
            user = None

            student = (
                Student.objects
                .filter(student_code=code, user__isnull=False)
                .select_related("user")
                .first()
            )
            if student:
                user = student.user

            if not user:
                trainer = (
                    Trainer.objects
                    .filter(trainer_code=code, user__isnull=False)
                    .select_related("user")
                    .first()
                )
                if trainer:
                    user = trainer.user

            if not user:
                raise serializers.ValidationError(
                    {"email": "Nenhuma conta encontrada para este código."}
                )

            attrs[self.username_field] = user.email

        data = super().validate(attrs)
        data["user"] = UserMeSerializer(self.user).data
        data["must_change_password"] = self.user.must_change_password
        data["memberships"] = MembershipSerializer(
            self.user.memberships.filter(is_active=True).select_related("institution"),
            many=True,
        ).data
        return data


class MembershipSerializer(serializers.ModelSerializer):
    institution_id   = serializers.UUIDField(source="institution.id",   read_only=True)
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "role", "institution_id", "institution_name", "is_active", "joined_at"]
        read_only_fields = fields


class UserMeSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    def get_email(self, obj):
        # Placeholder emails for code-only users are never exposed to the client
        if obj.email.endswith("@local.academico"):
            return ""
        return obj.email

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "is_active", "must_change_password", "created_at"]
        read_only_fields = ["id", "full_name", "is_active", "must_change_password", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "is_active", "memberships", "created_at"]
        read_only_fields = ["id", "created_at"]


class UserCreateSerializer(serializers.Serializer):
    email     = serializers.EmailField()
    password  = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(required=False, allow_blank=True, default="")
    role      = serializers.ChoiceField(choices=Membership.Role.choices)


class UserUpdateMeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
