from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import Membership


class MembershipJWTAuthentication(JWTAuthentication):
    """
    Extends JWTAuthentication to resolve the active Membership from the
    X-Institution-Id header and attach it to request.membership.

    - With JWT + X-Institution-Id: authenticates user AND loads membership.
    - With JWT only (e.g. /auth/me/, /auth/logout/): authenticates user,
      sets request.membership = None. Views that need membership will fail
      naturally if they try to access it without the header.
    - Without JWT: returns None (unauthenticated, normal DRF behaviour).
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result
        institution_id = request.headers.get("X-Institution-Id")

        if institution_id:
            try:
                membership = Membership.objects.select_related("institution").get(
                    user=user,
                    institution_id=institution_id,
                    is_active=True,
                )
            except Membership.DoesNotExist:
                raise AuthenticationFailed(
                    "No active membership found for this user at the specified institution."
                )
            if not membership.institution.is_verified:
                raise AuthenticationFailed(
                    "INSTITUTION_NOT_VERIFIED: A sua instituição ainda não foi verificada. "
                    "Consulte o email de registo para ativar a sua conta."
                )
            request.membership = membership
        else:
            request.membership = None

        return user, token
