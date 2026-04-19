from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "student_code",
        "institution",
        "is_active",
        "enrolled_at",
    )
    list_filter = ("is_active", "institution")
    search_fields = ("full_name", "student_code")
    readonly_fields = ("id", "enrolled_at", "updated_at")
    raw_id_fields = ("user",)
    fieldsets = (
        (None, {"fields": ("id", "institution", "user", "is_active")}),
        (
            "Profile",
            {"fields": ("full_name", "student_code", "birth_date", "phone", "address")},
        ),
        ("Dates", {"fields": ("enrolled_at", "updated_at")}),
    )
