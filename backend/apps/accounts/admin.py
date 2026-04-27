from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Membership


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "full_name", "is_active", "is_staff", "created_at")
    list_filter = ("is_active", "is_staff")
    search_fields = ("email", "full_name")
    ordering = ("email",)
    readonly_fields = ("id", "created_at", "updated_at", "last_login")

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        (_("Profile"), {"fields": ("full_name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "full_name",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "institution", "role", "is_active", "joined_at")
    list_filter = ("role", "is_active", "institution")
    search_fields = ("user__email", "user__full_name")
    readonly_fields = ("id", "joined_at", "updated_at")
    raw_id_fields = ("user",)
    fieldsets = (
        (None, {"fields": ("id", "user", "institution", "role", "is_active")}),
        ("Dates", {"fields": ("joined_at", "updated_at")}),
    )
