from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsPagination(PageNumberPagination):
    """
    Default paginator for all list endpoints.

    Query parameters:
      ?page=2          — page number (1-indexed)
      ?page_size=50    — override page size (capped at MAX_PAGE_SIZE)

    Response envelope:
      {
        "count":    <total records>,
        "pages":    <total pages>,
        "page":     <current page number>,
        "next":     <url | null>,
        "previous": <url | null>,
        "results":  [...]
      }
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "pages": self.page.paginator.num_pages,
                "page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "pages": {"type": "integer"},
                "page": {"type": "integer"},
                "next": {"type": "string", "nullable": True},
                "previous": {"type": "string", "nullable": True},
                "results": schema,
            },
        }
