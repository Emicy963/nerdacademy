from rest_framework.exceptions import ValidationError, NotFound

from .models import Trainer


class TrainerService:

    @staticmethod
    def create_trainer(institution, full_name: str, **kwargs) -> Trainer:
        trainer = Trainer.objects.create(
            institution=institution,
            full_name=full_name,
            **kwargs,
        )
        return trainer

    @staticmethod
    def get_trainer(trainer_id: str, institution) -> Trainer:
        try:
            return Trainer.objects.select_related("institution", "user").get(
                id=trainer_id,
                institution=institution,
            )
        except Trainer.DoesNotExist:
            raise NotFound("Trainer not found.")

    @staticmethod
    def update_trainer(trainer: Trainer, data: dict) -> Trainer:
        allowed = {"full_name", "specialization", "phone", "bio", "is_active"}
        for field, value in data.items():
            if field in allowed:
                setattr(trainer, field, value)
        trainer.save()
        return trainer

    @staticmethod
    def deactivate_trainer(trainer: Trainer) -> Trainer:
        trainer.is_active = False
        trainer.save()
        return trainer

    @staticmethod
    def list_trainers(institution, search: str = None, is_active: bool = None):
        qs = Trainer.objects.select_related("user").filter(institution=institution)
        if search:
            qs = qs.filter(full_name__icontains=search) | qs.filter(
                specialization__icontains=search
            )
            qs = qs.filter(institution=institution)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs.order_by("full_name")

    @staticmethod
    def get_trainer_by_user(user) -> Trainer:
        try:
            return Trainer.objects.select_related("institution").get(user=user)
        except Trainer.DoesNotExist:
            raise NotFound("Trainer profile not found for this user.")

    @staticmethod
    def link_user(trainer: Trainer, user) -> Trainer:
        """Link a User account to a Trainer profile."""
        if trainer.institution_id != user.institution_id:
            raise ValidationError(
                {"user": "User must belong to the same institution as the trainer."}
            )
        if user.role != "trainer":
            raise ValidationError(
                {
                    "user": 'Only users with role "trainer" can be linked to a trainer profile.'
                }
            )
        if Trainer.objects.filter(user=user).exclude(id=trainer.id).exists():
            raise ValidationError(
                {"user": "This user is already linked to another trainer profile."}
            )
        trainer.user = user
        trainer.save()
        return trainer

    @staticmethod
    def get_trainer_classes(trainer: Trainer):
        """Return all classes assigned to this trainer."""
        return trainer.classes.select_related("course", "institution").order_by(
            "-start_date"
        )
