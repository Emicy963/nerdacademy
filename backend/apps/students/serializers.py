from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = [
            "id",
            "institution",
            "full_name",
            "student_code",
            "birth_date",
            "phone",
            "address",
            "is_active",
            "enrolled_at",
            "updated_at",
        ]
        read_only_fields = ["id", "institution", "enrolled_at", "updated_at"]


class StudentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ["full_name", "student_code", "birth_date", "phone", "address"]

    def validate_student_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Student code cannot be blank.")
        return value.strip().upper()


class StudentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ["full_name", "birth_date", "phone", "address", "is_active"]


class StudentPublicSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "full_name",
            "student_code",
            "institution_name",
            "birth_date",
            "phone",
            "is_active",
        ]
        read_only_fields = fields


class StudentSummarySerializer(serializers.ModelSerializer):
    """Compact read-only serializer for embedding in other responses."""

    class Meta:
        model = Student
        fields = ["id", "full_name", "student_code"]
        read_only_fields = fields
