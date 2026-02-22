"""
Django management command to bootstrap a new institution with its first admin user.

Usage:
    python manage.py create_institution

    # Non-interactive (CI/scripts):
    python manage.py create_institution \\
        --name "CINFOTEC Huambo" \\
        --slug "cinfotec-huambo" \\
        --country "Angola" \\
        --admin-email "admin@cinfotec.ao" \\
        --admin-password "s3cr3t"
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Create a new institution and its first admin user."

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str, help="Institution full name")
        parser.add_argument(
            "--slug",
            type=str,
            help="URL-friendly identifier (e.g. cinfotec-huambo)",
        )
        parser.add_argument(
            "--country",
            type=str,
            default="Angola",
            help="Country (default: Angola)",
        )
        parser.add_argument("--admin-email", type=str, help="Admin user email")
        parser.add_argument("--admin-password", type=str, help="Admin user password")

    def handle(self, *args, **options):
        # ── Collect inputs ────────────────────────────────────────────────────
        name = options["name"] or self._prompt("Institution name")
        slug = options["slug"] or self._prompt(
            "Institution slug (e.g. cinfotec-huambo)"
        )
        country = options["country"] or self._prompt("Country", default="Angola")
        admin_email = options["admin_email"] or self._prompt("Admin email")
        admin_password = options["admin_password"] or self._prompt(
            "Admin password", secret=True
        )

        # ── Validate ──────────────────────────────────────────────────────────
        if not all([name, slug, admin_email, admin_password]):
            raise CommandError(
                "All fields are required: name, slug, admin-email, admin-password."
            )

        if len(admin_password) < 8:
            raise CommandError("Admin password must be at least 8 characters.")

        # ── Create in a single transaction ────────────────────────────────────
        try:
            with transaction.atomic():
                institution, admin = self._create(
                    name=name,
                    slug=slug,
                    country=country,
                    admin_email=admin_email,
                    admin_password=admin_password,
                )
        except Exception as exc:
            raise CommandError(str(exc)) from exc

        # ── Report ────────────────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Institution created successfully"))
        self.stdout.write(f"  ID   : {institution.id}")
        self.stdout.write(f"  Name : {institution.name}")
        self.stdout.write(f"  Slug : {institution.slug}")
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Admin user created successfully"))
        self.stdout.write(f"  ID    : {admin.id}")
        self.stdout.write(f"  Email : {admin.email}")
        self.stdout.write(f"  Role  : {admin.role}")
        self.stdout.write("")
        self.stdout.write("You can now log in at: POST /api/auth/login/")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _create(self, name, slug, country, admin_email, admin_password):
        """
        Delegates to the service layer — no direct ORM here.
        Imports are deferred so Django apps are fully loaded before use.
        """
        from apps.institutions.services import InstitutionService
        from apps.accounts.services import UserService

        institution = InstitutionService.create_institution(
            name=name,
            slug=slug,
            country=country,
        )

        admin = UserService.create_user(
            institution=institution,
            email=admin_email,
            password=admin_password,
            role="admin",
        )

        return institution, admin

    def _prompt(self, label: str, default: str = "", secret: bool = False) -> str:
        """Interactive prompt with optional default and hidden input."""
        import getpass

        display = f"{label} [{default}]: " if default else f"{label}: "
        if secret:
            value = getpass.getpass(display)
        else:
            value = input(display).strip()
        return value or default
