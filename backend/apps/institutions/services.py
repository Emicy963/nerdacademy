from rest_framework.exceptions import ValidationError, NotFound
from .models import Institution


class InstitutionService:

    @staticmethod
    def create_institution(name: str, slug: str, **kwargs) -> Institution:
        if Institution.objects.filter(slug=slug).exists():
            raise ValidationError(
                {"slug": f'Institution with slug "{slug}" already exists.'}
            )
        return Institution.objects.create(name=name, slug=slug, **kwargs)

    @staticmethod
    def get_institution(institution_id: str) -> Institution:
        try:
            return Institution.objects.get(id=institution_id)
        except Institution.DoesNotExist:
            raise NotFound("Institution not found.")

    @staticmethod
    def update_institution(institution: Institution, data: dict) -> Institution:
        allowed = {"name", "email", "phone", "address", "is_active"}
        for field, value in data.items():
            if field in allowed:
                setattr(institution, field, value)
        institution.save()
        return institution

    @staticmethod
    def list_institutions():
        return Institution.objects.all().order_by("name")
