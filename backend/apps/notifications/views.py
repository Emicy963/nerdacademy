from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import NotificationSerializer
from .services import NotificationService


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = NotificationService.list_recent(request.user)
        unread_count  = NotificationService.unread_count(request.user)
        return Response({
            "unread_count": unread_count,
            "results": NotificationSerializer(notifications, many=True).data,
        })


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        updated = NotificationService.mark_read(pk, request.user)
        if not updated:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        NotificationService.mark_all_read(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
