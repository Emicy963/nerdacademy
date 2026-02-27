from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "institution",
            "institution_name",
            "name",
            "code",
            "description",
            "total_hours",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "institution",
            "institution_name",
            "created_at",
            "updated_at",
        ]


class CourseCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ["name", "code", "description", "total_hours"]

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Course code cannot be blank.")
        return value.strip().upper()

    def validate_total_hours(self, value):
        if value < 0:
            raise serializers.ValidationError("Total hours cannot be negative.")
        return value


class CourseUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ["name", "description", "total_hours", "is_active"]

    def validate_total_hours(self, value):
        if value < 0:
            raise serializers.ValidationError("Total hours cannot be negative.")
        return value


class CourseSummarySerializer(serializers.ModelSerializer):
    """Compact read-only serializer for embedding in class responses."""

    class Meta:
        model = Course
        fields = ["id", "name", "code", "total_hours"]
        read_only_fields = fields
