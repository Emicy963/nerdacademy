import re
from datetime import date

from rest_framework.exceptions import ValidationError, NotFound

from .models import Institution


class InstitutionService:

    @staticmethod
    def create_institution(name: str, slug: str, **kwargs) -> Institution:
        if Institution.objects.filter(slug=slug).exists():
            raise ValidationError(
                {"slug": f'Institution with slug "{slug}" already exists.'}
            )
        inst = Institution(name=name, slug=slug, **kwargs)
        if not inst.institution_prefix:
            inst.institution_prefix = InstitutionService._derive_prefix(name)
        inst.save()
        return inst

    @staticmethod
    def get_institution(institution_id: str) -> Institution:
        try:
            return Institution.objects.get(id=institution_id)
        except Institution.DoesNotExist:
            raise NotFound("Institution not found.")

    @staticmethod
    def update_institution(institution: Institution, data: dict) -> Institution:
        allowed = {"name", "institution_prefix", "email", "phone", "address", "is_active"}
        for field, value in data.items():
            if field in allowed:
                setattr(institution, field, value)
        if institution.institution_prefix:
            institution.institution_prefix = institution.institution_prefix.upper()
        institution.save()
        return institution

    @staticmethod
    def list_institutions():
        return Institution.objects.all().order_by("name")

    # ── Code generation ────────────────────────────────────────────

    @staticmethod
    def get_prefix(institution: Institution) -> str:
        """
        Returns the institution prefix used for code generation.
        If institution_prefix is blank, derives it from the institution name:
          - Multi-word: initials of up to 3 words  →  "Centro Info Tec" → "CIT"
          - Single word: first 3 letters            →  "Cinfotec" → "CIN"
        """
        if institution.institution_prefix:
            return institution.institution_prefix.upper()
        return InstitutionService._derive_prefix(institution.name)

    @staticmethod
    def generate_student_code(institution: Institution, year: int = None) -> str:
        """
        Returns the next available student code for the given institution and year.
        Format: {PREFIX}{YEAR}{SEQ:04d}  →  e.g. CIN20260001
        """
        from apps.students.models import Student

        if year is None:
            year = date.today().year

        prefix = InstitutionService.get_prefix(institution)
        pattern = f"{prefix}{year}"

        existing = (
            Student.objects.filter(
                institution=institution,
                student_code__startswith=pattern,
            )
            .values_list("student_code", flat=True)
        )
        seq = InstitutionService._next_seq(pattern, existing)
        return f"{pattern}{seq:04d}"

    @staticmethod
    def generate_trainer_code(institution: Institution, year: int = None) -> str:
        """
        Returns the next available trainer code for the given institution and year.
        Format: {PREFIX}F{YEAR}{SEQ:04d}  →  e.g. CINF20260001
        The "F" suffix differentiates trainers from students.
        """
        from apps.trainers.models import Trainer

        if year is None:
            year = date.today().year

        prefix = InstitutionService.get_prefix(institution) + "F"
        pattern = f"{prefix}{year}"

        existing = (
            Trainer.objects.filter(
                institution=institution,
                trainer_code__startswith=pattern,
            )
            .values_list("trainer_code", flat=True)
        )
        seq = InstitutionService._next_seq(pattern, existing)
        return f"{pattern}{seq:04d}"

    # ── Self-service registration ──────────────────────────────────

    @staticmethod
    def register(institution_name: str, admin_name: str, email: str, password: str) -> dict:
        """
        Public self-service signup. Atomically creates:
          Institution (unverified) → User (admin) → Membership.
        Sends a verification email; the institution is only active after verification.
        """
        import secrets
        from django.db import transaction
        from django.utils.text import slugify
        from django.conf import settings
        from apps.accounts.services import UserService, MembershipService
        from apps.accounts.emails import send_institution_verification

        with transaction.atomic():
            base_slug = slugify(institution_name) or "institution"
            slug, counter = base_slug, 2
            while Institution.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            verification_token = secrets.token_urlsafe(32)
            institution = InstitutionService.create_institution(
                name=institution_name,
                slug=slug,
                email=email,
                is_verified=False,
                verification_token=verification_token,
            )
            user = UserService.create_user(
                email=email,
                password=password,
                full_name=admin_name,
                must_change_password=False,
            )
            MembershipService.create_membership(
                user=user,
                institution=institution,
                role="admin",
            )

        verify_url = (
            f"{settings.FRONTEND_URL}/pages/verify-institution.html"
            f"#{verification_token}"
        )
        send_institution_verification(user, institution, verify_url)

        return {
            "detail": "Registo efetuado! Enviámos um email de verificação para ativar a sua instituição.",
            "email": email,
        }

    @staticmethod
    def verify_institution(token: str) -> "Institution":
        """Activate an institution using its verification token."""
        try:
            institution = Institution.objects.get(
                verification_token=token,
                is_verified=False,
            )
        except Institution.DoesNotExist:
            raise ValidationError({"token": "Token de verificação inválido ou já utilizado."})

        institution.is_verified = True
        institution.verification_token = None
        institution.save(update_fields=["is_verified", "verification_token"])
        return institution

    # ── Private helpers ────────────────────────────────────────────

    @staticmethod
    def _derive_prefix(name: str) -> str:
        words = name.split()
        if len(words) >= 2:
            return "".join(w[0] for w in words[:3]).upper()
        return re.sub(r"[^A-Z]", "", name.upper())[:3] or name[:3].upper()

    @staticmethod
    def _next_seq(pattern: str, existing_codes) -> int:
        """
        Finds the lowest unused sequence number given a list of existing codes
        that start with *pattern*. Handles gaps caused by deletions.
        """
        used = set()
        suffix_len = 4  # always 4-digit sequence
        for code in existing_codes:
            tail = code[len(pattern):]
            if tail.isdigit() and len(tail) == suffix_len:
                used.add(int(tail))
        seq = 1
        while seq in used:
            seq += 1
        return seq
