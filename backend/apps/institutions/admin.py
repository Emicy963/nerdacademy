from django.contrib import admin
from .models import Institution


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "email",
        "province",
        "is_verified",
        "is_active",
        "created_at",
    )
    list_filter = ("is_verified", "is_active")
    search_fields = ("name", "slug", "email")
    readonly_fields = ("id", "verification_token", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("id", "name", "slug", "is_active")}),
        ("Verification", {"fields": ("is_verified", "verification_token")}),
        ("Contact", {"fields": ("email", "phone", "province", "address")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
