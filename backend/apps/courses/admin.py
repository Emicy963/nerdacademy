from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "institution",
        "total_hours",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "institution")
    search_fields = ("name", "code")
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("id", "institution", "is_active")}),
        ("Course", {"fields": ("name", "code", "description", "total_hours")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
