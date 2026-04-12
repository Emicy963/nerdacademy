from rest_framework import serializers
from .models import Trainer


class TrainerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trainer
        fields = [
            "id",
            "institution",
            "full_name",
            "specialization",
            "phone",
            "bio",
            "is_active",
            "hired_at",
            "updated_at",
        ]
        read_only_fields = ["id", "institution", "hired_at", "updated_at"]


class TrainerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trainer
        fields = ["full_name", "specialization", "phone", "bio"]


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
        fields = ["id", "full_name", "specialization"]
        read_only_fields = fields
