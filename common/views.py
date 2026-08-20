from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        print("LOGGED IN USER:", request.user)
        print("USER EMAIL:", request.user.email)
        print("USER ID:", request.user.id)

        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 10

        page = paginator.paginate_queryset(
            notifications,
            request
        )

        serializer = NotificationSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class NotificationMarkReadAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        try:
            notification = Notification.objects.get(
                id=pk,
                user=request.user
            )
        except Notification.DoesNotExist:
            return Response(
                {"message": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response(
            {
                "message": "Notification marked as read."
            },
            status=status.HTTP_200_OK
        )


class NotificationMarkAllReadAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response(
            {
                "message": "All notifications marked as read.",
                "updated_count": updated_count
            },
            status=status.HTTP_200_OK
        )
