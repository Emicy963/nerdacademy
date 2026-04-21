from rest_framework.exceptions import ValidationError, NotFound

from .models import Trainer


class TrainerService:

    @staticmethod
    def create_trainer(
        institution, full_name: str, trainer_code: str = None, email: str = "", **kwargs
    ) -> tuple:
        from apps.institutions.services import InstitutionService
        from apps.accounts.services import UserService

        if not trainer_code:
            trainer_code = InstitutionService.generate_trainer_code(institution)
        else:
            trainer_code = trainer_code.strip().upper()

        trainer = Trainer.objects.create(
            institution=institution,
            full_name=full_name,
            trainer_code=trainer_code,
            **kwargs,
        )

        temp_password = None
        if email:
            user, temp_password = UserService.create_managed_user(
                email=email, full_name=full_name, institution=institution, role="trainer"
            )
            trainer.user = user
            trainer.save(update_fields=["user"])
            from apps.accounts.emails import send_welcome_trainer
            send_welcome_trainer(trainer, temp_password)

        return trainer, temp_password

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
        from django.db.models import Q

        qs = Trainer.objects.select_related("user").filter(institution=institution)
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search) | Q(specialization__icontains=search)
            )
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs.order_by("full_name")

    @staticmethod
    def get_trainer_by_user(user, institution) -> Trainer:
        """
        Get the trainer profile for a user within a specific institution.
        A user can be a trainer at multiple institutions.
        """
        try:
            return Trainer.objects.select_related("institution").get(
                user=user,
                institution=institution,
            )
        except Trainer.DoesNotExist:
            raise NotFound(
                "Trainer profile not found for this user at this institution."
            )

    @staticmethod
    def link_user(trainer: Trainer, user, membership) -> Trainer:
        """
        Link a User account to a Trainer profile.
        Validates via Membership that the user has a trainer role
        at this institution.
        """
        if membership.institution_id != trainer.institution_id:
            raise ValidationError(
                {
                    "user": "User must have a membership at the same institution as the trainer."
                }
            )
        if membership.role != "trainer":
            raise ValidationError(
                {
                    "user": 'Only users with role "trainer" can be linked to a trainer profile.'
                }
            )
        if (
            Trainer.objects.filter(user=user, institution=trainer.institution)
            .exclude(id=trainer.id)
            .exists()
        ):
            raise ValidationError(
                {
                    "user": "This user is already linked to another trainer profile at this institution."
                }
            )
        trainer.user = user
        trainer.save()
        return trainer

    @staticmethod
    def get_trainer_classes(trainer: Trainer):
        return trainer.classes.select_related("course", "institution").order_by(
            "-start_date"
        )
