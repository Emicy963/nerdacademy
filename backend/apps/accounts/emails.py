from django.conf import settings
from django.core.mail import send_mail


def _send(subject: str, message: str, to: str):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to],
        fail_silently=True,
    )


def send_welcome_student(student, temp_password: str):
    """Sent when an admin creates a student with an email."""
    if not student.user_id or not student.user.email:
        return
    _send(
        subject=f"Bem-vindo ao Acadêmico — {student.institution.name}",
        message=(
            f"Olá {student.full_name},\n\n"
            f"A sua conta de estudante foi criada em {student.institution.name}.\n\n"
            f"Email: {student.user.email}\n"
            f"Código de estudante: {student.student_code}\n"
            f"Senha temporária: {temp_password}\n\n"
            "Por favor altere a sua senha no primeiro acesso.\n\n"
            "Acadêmico"
        ),
        to=student.user.email,
    )


def send_welcome_trainer(trainer, temp_password: str):
    """Sent when an admin creates a trainer with an email."""
    if not trainer.user_id or not trainer.user.email:
        return
    _send(
        subject=f"Bem-vindo ao Acadêmico — {trainer.institution.name}",
        message=(
            f"Olá {trainer.full_name},\n\n"
            f"A sua conta de formador foi criada em {trainer.institution.name}.\n\n"
            f"Email: {trainer.user.email}\n"
            f"Código de formador: {trainer.trainer_code}\n"
            f"Senha temporária: {temp_password}\n\n"
            "Por favor altere a sua senha no primeiro acesso.\n\n"
            "Acadêmico"
        ),
        to=trainer.user.email,
    )


def send_password_reset(user, temp_password: str):
    """Sent when an admin resets a user's password."""
    if not user.email:
        return
    _send(
        subject="Acadêmico — Senha redefinida",
        message=(
            f"Olá {user.full_name or user.email},\n\n"
            "A sua senha foi redefinida por um administrador.\n\n"
            f"Nova senha temporária: {temp_password}\n\n"
            "Por favor altere a sua senha no próximo acesso.\n\n"
            "Acadêmico"
        ),
        to=user.email,
    )
