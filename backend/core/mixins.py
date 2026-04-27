from rest_framework.response import Response
from rest_framework import status
from core.pagination import StandardResultsPagination


class PaginatedListMixin:
    """
    Adds paginated list support to any APIView.

    Usage in a view's GET handler:
        def get(self, request):
            qs = MyService.list_things(institution=request.user.institution)
            return self.paginate(request, qs, MySerializer)
    """

    pagination_class = StandardResultsPagination

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            self._paginator = self.pagination_class()
        return self._paginator

    def paginate(self, request, queryset, serializer_class, **serializer_kwargs):
        """
        Paginate a queryset and return a paginated Response.
        Falls back to a full list when the client sends ?page_size=0.
        """
        page = self.paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = serializer_class(page, many=True, **serializer_kwargs)
            return self.paginator.get_paginated_response(serializer.data)
        serializer = serializer_class(queryset, many=True, **serializer_kwargs)
        return Response(serializer.data)


class InstitutionQuerysetMixin:
    """
    Automatically filters all querysets by the authenticated
    user's institution. Apply to any ViewSet to enforce
    multi-tenant data isolation at the queryset level.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if (
            user.is_authenticated
            and hasattr(user, "institution_id")
            and user.institution_id
        ):
            return qs.filter(institution_id=user.institution_id)
        return qs.none()

    def perform_create(self, serializer):
        """Automatically inject institution on create."""
        serializer.save(institution=self.request.user.institution)
