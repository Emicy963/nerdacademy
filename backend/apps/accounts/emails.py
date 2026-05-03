import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _send(subject: str, message: str, to: str):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error("Failed to send email to %s — subject: %s — error: %s", to, subject, exc)


def send_welcome_student(student, temp_password: str):
    """Sent when an admin creates a student with an email."""
    if not student.user_id or not student.user.email:
        return
    _send(
        subject=f"Bem-vindo ao Matrika — {student.institution.name}",
        message=(
            f"Olá {student.full_name},\n\n"
            f"A sua conta de estudante foi criada em {student.institution.name}.\n\n"
            f"Email: {student.user.email}\n"
            f"Código de estudante: {student.student_code}\n"
            f"Senha temporária: {temp_password}\n\n"
            "Por favor altere a sua senha no primeiro acesso.\n\n"
            "Matrika"
        ),
        to=student.user.email,
    )


def send_welcome_trainer(trainer, temp_password: str):
    """Sent when an admin creates a trainer with an email."""
    if not trainer.user_id or not trainer.user.email:
        return
    _send(
        subject=f"Bem-vindo ao Matrika — {trainer.institution.name}",
        message=(
            f"Olá {trainer.full_name},\n\n"
            f"A sua conta de formador foi criada em {trainer.institution.name}.\n\n"
            f"Email: {trainer.user.email}\n"
            f"Código de formador: {trainer.trainer_code}\n"
            f"Senha temporária: {temp_password}\n\n"
            "Por favor altere a sua senha no primeiro acesso.\n\n"
            "Matrika"
        ),
        to=trainer.user.email,
    )


def send_password_reset_link(user, reset_url: str):
    """Sent when a user requests a self-service password reset link."""
    _send(
        subject="Matrika — Redefinição de palavra-passe",
        message=(
            f"Olá {user.full_name or user.email},\n\n"
            "Recebemos um pedido para redefinir a palavra-passe da sua conta.\n\n"
            f"Clique no link abaixo para definir uma nova palavra-passe:\n{reset_url}\n\n"
            "Este link é válido por 24 horas. Se não fez este pedido, ignore este email.\n\n"
            "Matrika"
        ),
        to=user.email,
    )


def send_institution_verification(user, institution, verify_url: str):
    """Sent after self-service institution registration to verify the admin email."""
    _send(
        subject="Matrika — Verifique a sua conta",
        message=(
            f"Olá {user.full_name or user.email},\n\n"
            f"Obrigado por registar a instituição «{institution.name}» na plataforma Matrika.\n\n"
            "Para ativar a sua conta, clique no link abaixo:\n"
            f"{verify_url}\n\n"
            "Este link é válido enquanto a verificação não for concluída.\n"
            "Se não criou esta conta, ignore este email.\n\n"
            "Matrika"
        ),
        to=user.email,
    )


def send_password_reset(user, temp_password: str):
    """Sent when an admin resets a user's password."""
    if not user.email:
        return
    _send(
        subject="Matrika — Senha redefinida",
        message=(
            f"Olá {user.full_name or user.email},\n\n"
            "A sua senha foi redefinida por um administrador.\n\n"
            f"Nova senha temporária: {temp_password}\n\n"
            "Por favor altere a sua senha no próximo acesso.\n\n"
            "Matrika"
        ),
        to=user.email,
    )
