import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Grade(models.Model):

    class AssessmentType(models.TextChoices):
        CONTINUOUS = "continuous", "Continuous Assessment"
        EXAM = "exam", "Exam"
        PRACTICAL = "practical", "Practical Work"
        PROJECT = "project", "Project"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        "institutions.Institution",
        on_delete=models.CASCADE,
        related_name="grades",
    )
    enrollment = models.ForeignKey(
        "classes.Enrollment",
        on_delete=models.CASCADE,
        related_name="grades",
    )
    assessment_type = models.CharField(
        max_length=15,
        choices=AssessmentType.choices,
        default=AssessmentType.CONTINUOUS,
    )
    value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    max_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20.00,
        validators=[MinValueValidator(0.01)],
    )
    assessed_at = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "grades"
        ordering = ["-assessed_at", "assessment_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "assessment_type"],
                name="unique_grade_per_assessment_type",
            )
        ]

    def __str__(self):
        return (
            f"{self.enrollment.student.full_name} — "
            f"{self.assessment_type}: {self.value}/{self.max_value}"
        )

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.value is not None and self.max_value is not None:
            if self.value > self.max_value:
                raise ValidationError({"value": "Grade value cannot exceed max_value."})
