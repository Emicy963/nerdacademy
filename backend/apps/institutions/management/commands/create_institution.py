import getpass
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Bootstrap a new institution with an admin user."

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str, help="Institution name")
        parser.add_argument("--slug", type=str, help="Institution slug")
        parser.add_argument("--province", type=str, help="Province (e.g. Huambo)")
        parser.add_argument("--admin-email", type=str, help="Admin email")
        parser.add_argument("--admin-password", type=str, help="Admin password")

    def _prompt(self, label, default=None, secret=False):
        if default:
            label = f"{label} [{default}]"
        label += ": "
        if secret:
            value = getpass.getpass(label)
        else:
            value = input(label)
        return value.strip() or default or ""

    def handle(self, *args, **options):
        from apps.institutions.services import InstitutionService
        from apps.accounts.services import UserService, MembershipService

        name = options["name"] or self._prompt("Institution name")
        slug = options["slug"] or self._prompt(
            "Institution slug (e.g. cinfotec-huambo)"
        )
        province = options["province"] or self._prompt("Province (e.g. Huambo, Luanda)")
        email = options["admin_email"] or self._prompt("Admin email")
        password = options["admin_password"] or self._prompt(
            "Admin password", secret=True
        )

        if not all([name, slug, email, password]):
            raise CommandError("Name, slug, admin email and password are all required.")

        try:
            with transaction.atomic():
                institution = InstitutionService.create_institution(
                    name=name,
                    slug=slug,
                    province=province,
                )

                # Create or retrieve the global user
                try:
                    user = UserService.get_user_by_email(email)
                    self.stdout.write(f"  Using existing user: {email}")
                except Exception:
                    user = UserService.create_user(
                        email=email,
                        password=password,
                        full_name="Admin",
                    )

                # Grant admin membership at the new institution
                MembershipService.create_membership(
                    user=user,
                    institution=institution,
                    role="admin",
                )

        except Exception as exc:
            raise CommandError(str(exc))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nInstitution '{name}' created successfully.\n"
                f"  Admin: {email}\n"
                f"  Slug:  {slug}\n"
                f"  Log in at /api/auth/login/ with X-Institution-ID: {institution.id}\n"
            )
        )
