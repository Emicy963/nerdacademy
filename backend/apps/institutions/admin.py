from django.contrib import admin
from .models import Institution


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "province",
        "email",
        "phone",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "email")
    readonly_fields = ("id", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("id", "name", "slug", "is_active")}),
        ("Contact", {"fields": ("email", "phone", "province", "address")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
