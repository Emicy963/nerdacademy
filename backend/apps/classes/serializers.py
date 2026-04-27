from rest_framework import serializers

from apps.courses.serializers import CourseSummarySerializer
from apps.trainers.serializers import TrainerSummarySerializer
from apps.students.serializers import StudentSummarySerializer
from .models import Class, Enrollment


class ClassSerializer(serializers.ModelSerializer):
    course = CourseSummarySerializer(read_only=True)
    trainer = TrainerSummarySerializer(read_only=True)
    institution_name = serializers.CharField(source="institution.name", read_only=True)
    enrollment_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = [
            "id",
            "institution",
            "institution_name",
            "course",
            "trainer",
            "name",
            "status",
            "start_date",
            "end_date",
            "enrollment_count",
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

    def get_enrollment_count(self, obj):
        return obj.enrollments.filter(status="active").count()


class ClassCreateSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
    trainer_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        if data["start_date"] >= data["end_date"]:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )
        return data


class ClassUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    trainer_id = serializers.UUIDField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    status = serializers.ChoiceField(choices=Class.Status.choices, required=False)


class ClassDetailSerializer(ClassSerializer):
    """Extended serializer that includes full enrollment list."""

    enrollments = serializers.SerializerMethodField()

    class Meta(ClassSerializer.Meta):
        fields = ClassSerializer.Meta.fields + ["enrollments"]

    def get_enrollments(self, obj):
        active_enrollments = obj.enrollments.select_related("student").filter(
            status="active"
        )
        return EnrollmentSerializer(active_enrollments, many=True).data


class ClassSummarySerializer(serializers.ModelSerializer):
    """Compact read-only serializer — used by trainers and courses apps."""

    course_name = serializers.CharField(source="course.name", read_only=True)
    course_code = serializers.CharField(source="course.code", read_only=True)
    trainer_name = serializers.CharField(source="trainer.full_name", read_only=True)

    class Meta:
        model = Class
        fields = [
            "id",
            "name",
            "status",
            "start_date",
            "end_date",
            "course_name",
            "course_code",
            "trainer_name",
        ]
        read_only_fields = fields


class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSummarySerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "status", "enrolled_at", "updated_at"]
        read_only_fields = fields


class EnrollmentCreateSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    """Full enrollment with nested class and student info."""

    student = StudentSummarySerializer(read_only=True)
    class_name = serializers.CharField(source="class_instance.name", read_only=True)
    course_name = serializers.CharField(
        source="class_instance.course.name", read_only=True
    )
    trainer_name = serializers.CharField(
        source="class_instance.trainer.full_name", read_only=True
    )

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "class_name",
            "course_name",
            "trainer_name",
            "status",
            "enrolled_at",
            "updated_at",
        ]
        read_only_fields = fields
