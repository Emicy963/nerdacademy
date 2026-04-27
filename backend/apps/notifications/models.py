import uuid
from django.conf import settings
from django.db import models


class Notification(models.Model):

    class Type(models.TextChoices):
        ENROLLMENT = "enrollment", "Enrollment"
        GRADE      = "grade",      "Grade"
        SYSTEM     = "system",     "System"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type       = models.CharField(max_length=20, choices=Type.choices, default=Type.SYSTEM)
    title      = models.CharField(max_length=255)
    message    = models.TextField(blank=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.type}] {self.title} → {self.user_id}"
