import uuid
from django.db import models


class Class(models.Model):

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        "institutions.Institution",
        on_delete=models.CASCADE,
        related_name="classes",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        related_name="classes",
    )
    trainer = models.ForeignKey(
        "trainers.Trainer",
        on_delete=models.PROTECT,
        related_name="classes",
    )
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.OPEN
    )
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "classes"
        ordering = ["-start_date"]
        verbose_name_plural = "classes"

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def is_open(self):
        return self.status == self.Status.OPEN

    @property
    def is_closed(self):
        return self.status == self.Status.CLOSED


class Enrollment(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DROPPED = "dropped", "Dropped"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_instance = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="enrollments",
        db_column="class_id",
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "enrollments"
        ordering = ["enrolled_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["class_instance", "student"],
                name="unique_enrollment_per_class",
            )
        ]

    def __str__(self):
        return f"{self.student.full_name} → {self.class_instance.name}"
