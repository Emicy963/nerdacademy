from django.contrib import admin
from .models import Grade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = (
        "get_student",
        "get_class",
        "assessment_type",
        "value",
        "max_value",
        "assessed_at",
        "institution",
    )
    list_filter = ("assessment_type", "institution")
    search_fields = (
        "enrollment__student__full_name",
        "enrollment__class_instance__name",
    )
    readonly_fields = ("id", "institution", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("id", "institution", "enrollment")}),
        (
            "Grade",
            {
                "fields": (
                    "assessment_type",
                    "value",
                    "max_value",
                    "assessed_at",
                    "notes",
                )
            },
        ),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Student")
    def get_student(self, obj):
        return obj.enrollment.student.full_name

    @admin.display(description="Class")
    def get_class(self, obj):
        return obj.enrollment.class_instance.name
