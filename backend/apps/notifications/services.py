from .models import Notification


class NotificationService:

    @staticmethod
    def create(user, ntype: str, title: str, message: str = "") -> Notification:
        return Notification.objects.create(
            user=user, type=ntype, title=title, message=message
        )

    @staticmethod
    def list_recent(user, limit: int = 20):
        return Notification.objects.filter(user=user).order_by("-created_at")[:limit]

    @staticmethod
    def unread_count(user) -> int:
        return Notification.objects.filter(user=user, is_read=False).count()

    @staticmethod
    def mark_read(notification_id: str, user) -> int:
        return Notification.objects.filter(id=notification_id, user=user).update(is_read=True)

    @staticmethod
    def mark_all_read(user) -> int:
        return Notification.objects.filter(user=user, is_read=False).update(is_read=True)

    # ── Domain triggers ────────────────────────────────────────────────

    @staticmethod
    def notify_enrollment(enrollment) -> None:
        trainer = enrollment.class_instance.trainer
        if not trainer.user_id:
            return
        NotificationService.create(
            user=trainer.user,
            ntype=Notification.Type.ENROLLMENT,
            title=f"Novo aluno inscrito em {enrollment.class_instance.name}",
            message=f"{enrollment.student.full_name} inscreveu-se na turma.",
        )

    @staticmethod
    def notify_grade(grade) -> None:
        student = grade.enrollment.student
        if not student.user_id:
            return
        type_label = grade.get_assessment_type_display()
        NotificationService.create(
            user=student.user,
            ntype=Notification.Type.GRADE,
            title=f"Nova nota em {grade.enrollment.class_instance.name}",
            message=f"{type_label}: {grade.value}/{grade.max_value}",
        )
