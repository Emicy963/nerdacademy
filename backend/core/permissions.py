from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Grants access only to users with role 'admin'."""

    message = "Only institution admins can perform this action."

    def has_permission(self, request, view):
        membership = getattr(request, "membership", None)
        return bool(
            request.user
            and request.user.is_authenticated
            and membership
            and membership.role == "admin"
        )


class IsTrainerRole(BasePermission):
    """Grants access to admin and trainer roles."""

    message = "Only trainers or admins can perform this action."

    def has_permission(self, request, view):
        membership = getattr(request, "membership", None)
        return bool(
            request.user
            and request.user.is_authenticated
            and membership
            and membership.role in ("admin", "trainer")
        )


class IsStudentRole(BasePermission):
    """Grants access only to students."""

    message = "Only students can perform this action."

    def has_permission(self, request, view):
        membership = getattr(request, "membership", None)
        return bool(
            request.user
            and request.user.is_authenticated
            and membership
            and membership.role == "student"
        )


class IsInstitutionMember(BasePermission):
    """
    Object-level permission: ensures the object's institution
    matches the authenticated user's active membership institution.
    """

    message = "You do not have permission to access this resource."

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        membership = getattr(request, "membership", None)
        if not membership:
            return False
        obj_institution = getattr(obj, "institution_id", None)
        return obj_institution == membership.institution_id


class IsOwnerTrainer(BasePermission):
    """
    Ensures a trainer can only modify grades for their own classes.
    Admins bypass this check.
    """

    message = "You can only manage grades for your own classes."

    def has_object_permission(self, request, view, obj):
        membership = getattr(request, "membership", None)
        if membership and membership.role == "admin":
            return True
        try:
            return obj.enrollment.class_instance.trainer.user_id == request.user.id
        except AttributeError:
            return False
