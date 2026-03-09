#!/usr/bin/env python
"""
Management helper: creates an institution and its first admin user.
Usage: python create_institution.py
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")
django.setup()

from apps.institutions.models import Institution
from apps.institutions.services import InstitutionService
from apps.accounts.services import UserService


def main():
    print("=== Create Institution + Admin ===")

    name = input("Institution name: ").strip()
    slug = input("Institution slug (e.g. centro-angola): ").strip()
    country = input("Country [Angola]: ").strip() or "Angola"
    email = input("Admin email: ").strip()
    password = input("Admin password: ").strip()

    institution = InstitutionService.create_institution(
        name=name, slug=slug, country=country
    )
    print(f"Institution created: {institution.name} ({institution.id})")

    admin = UserService.create_user(
        institution=institution,
        email=email,
        password=password,
        role="admin",
    )
    print(f"Admin user created: {admin.email}")
    print("\nDone. You can now log in at POST /api/auth/login/")


if __name__ == "__main__":
    main()
