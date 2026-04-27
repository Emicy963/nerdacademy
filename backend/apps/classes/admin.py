from django.contrib import admin
from .models import Class, Enrollment


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    readonly_fields = ("id", "student", "status", "enrolled_at")
    fields = ("student", "status", "enrolled_at")
    can_delete = False


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "course",
        "trainer",
        "institution",
        "status",
        "start_date",
        "end_date",
    )
    list_filter = ("status", "institution", "course")
    search_fields = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [EnrollmentInline]
    fieldsets = (
        (None, {"fields": ("id", "institution", "status")}),
        ("Class", {"fields": ("name", "course", "trainer")}),
        ("Dates", {"fields": ("start_date", "end_date", "created_at", "updated_at")}),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "class_instance", "status", "enrolled_at")
    list_filter = ("status",)
    search_fields = ("student__full_name", "class_instance__name")
    readonly_fields = ("id", "enrolled_at", "updated_at")
