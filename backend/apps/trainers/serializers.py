from rest_framework import serializers
from .models import Trainer


class TrainerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trainer
        fields = [
            "id",
            "institution",
            "full_name",
            "trainer_code",
            "specialization",
            "phone",
            "bio",
            "is_active",
            "hired_at",
            "updated_at",
        ]
        read_only_fields = ["id", "institution", "trainer_code", "hired_at", "updated_at"]


class TrainerCreateSerializer(serializers.ModelSerializer):
    # Optional — auto-generated from institution prefix if omitted
    trainer_code = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = Trainer
        fields = ["full_name", "trainer_code", "specialization", "phone", "bio"]

    def validate_trainer_code(self, value):
        return value.strip().upper() if value and value.strip() else ""


class TrainerUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trainer
        fields = ["full_name", "specialization", "phone", "bio", "is_active"]


class TrainerPublicSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = Trainer
        fields = ["id", "full_name", "specialization", "institution_name", "bio"]
        read_only_fields = fields


class TrainerSummarySerializer(serializers.ModelSerializer):
    """Compact read-only serializer for embedding in class responses."""

    class Meta:
        model = Trainer
        fields = ["id", "full_name", "trainer_code", "specialization"]
        read_only_fields = fields
