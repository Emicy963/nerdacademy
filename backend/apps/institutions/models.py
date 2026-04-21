import uuid
from django.db import models


class Institution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    # 2-5 uppercase chars used as prefix for student/trainer codes (e.g. "CIN")
    # If blank, derived automatically from the first letters of the name.
    institution_prefix = models.CharField(max_length=5, blank=True, default="")
    province = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "institutions"
        ordering = ["name"]

    def __str__(self):
        return self.name
