from django.contrib import admin
from .models import Trainer


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "specialization",
        "institution",
        "is_active",
        "hired_at",
    )
    list_filter = ("is_active", "institution")
    search_fields = ("full_name", "specialization")
    readonly_fields = ("id", "hired_at", "updated_at")
    raw_id_fields = ("user",)
    fieldsets = (
        (None, {"fields": ("id", "institution", "user", "is_active")}),
        ("Profile", {"fields": ("full_name", "specialization", "phone", "bio")}),
        ("Dates", {"fields": ("hired_at", "updated_at")}),
    )
