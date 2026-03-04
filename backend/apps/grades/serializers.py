from decimal import Decimal
from rest_framework import serializers

from .models import Grade


class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source="enrollment.student.full_name", read_only=True
    )
    student_code = serializers.CharField(
        source="enrollment.student.student_code", read_only=True
    )
    class_name = serializers.CharField(
        source="enrollment.class_instance.name", read_only=True
    )
    course_name = serializers.CharField(
        source="enrollment.class_instance.course.name", read_only=True
    )

    class Meta:
        model = Grade
        fields = [
            "id",
            "institution",
            "enrollment",
            "student_name",
            "student_code",
            "class_name",
            "course_name",
            "assessment_type",
            "value",
            "max_value",
            "assessed_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "institution",
            "student_name",
            "student_code",
            "class_name",
            "course_name",
            "created_at",
            "updated_at",
        ]


class GradeLaunchSerializer(serializers.Serializer):
    enrollment_id = serializers.UUIDField()
    assessment_type = serializers.ChoiceField(choices=Grade.AssessmentType.choices)
    value = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal("0")
    )
    max_value = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal("0.01")
    )
    assessed_at = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, data):
        if data["value"] > data["max_value"]:
            raise serializers.ValidationError(
                {"value": "Grade value cannot exceed max_value."}
            )
        return data


class GradeUpdateSerializer(serializers.Serializer):
    value = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal("0"), required=False
    )
    max_value = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal("0.01"), required=False
    )
    assessed_at = serializers.DateField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        value = data.get("value")
        max_value = data.get("max_value")
        if value is not None and max_value is not None:
            if value > max_value:
                raise serializers.ValidationError(
                    {"value": "Grade value cannot exceed max_value."}
                )
        return data


class GradeReportEntrySerializer(serializers.Serializer):
    """Serializes a single student row in the class grade report."""

    class StudentInfoSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        full_name = serializers.CharField()
        student_code = serializers.CharField()

    class GradeRowSerializer(serializers.ModelSerializer):
        class Meta:
            model = Grade
            fields = [
                "id",
                "assessment_type",
                "value",
                "max_value",
                "assessed_at",
                "notes",
            ]

    enrollment_id = serializers.UUIDField()
    enrollment_status = serializers.CharField()
    student = StudentInfoSerializer()
    grades = serializers.SerializerMethodField()
    average = serializers.DecimalField(max_digits=5, decimal_places=2)

    def get_grades(self, obj):
        return self.GradeRowSerializer(obj["grades"], many=True).data


class MyGradeSerializer(serializers.ModelSerializer):
    """What a student sees when viewing their own grades."""

    class_name = serializers.CharField(
        source="enrollment.class_instance.name", read_only=True
    )
    course_name = serializers.CharField(
        source="enrollment.class_instance.course.name", read_only=True
    )
    trainer_name = serializers.CharField(
        source="enrollment.class_instance.trainer.full_name", read_only=True
    )

    class Meta:
        model = Grade
        fields = [
            "id",
            "assessment_type",
            "value",
            "max_value",
            "assessed_at",
            "class_name",
            "course_name",
            "trainer_name",
        ]
        read_only_fields = fields
