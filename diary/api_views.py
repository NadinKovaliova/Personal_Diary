from rest_framework import viewsets, permissions
from .models import DiaryEntry, Goal, WishListItem, Letter, UserAnalytics
from .serializers import (
    DiaryEntrySerializer, 
    GoalSerializer, 
    WishListItemSerializer,
    LetterSerializer,
    UserAnalyticsSerializer
)

class DiaryEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DiaryEntrySerializer
    queryset = DiaryEntry.objects.none()  # Default empty queryset

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user)

class GoalViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    queryset = Goal.objects.none()

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

class WishListItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishListItemSerializer
    queryset = WishListItem.objects.none()

    def get_queryset(self):
        return WishListItem.objects.filter(user=self.request.user)

class LetterViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LetterSerializer
    queryset = Letter.objects.none()

    def get_queryset(self):
        return Letter.objects.filter(user=self.request.user)

class UserAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserAnalyticsSerializer
    queryset = UserAnalytics.objects.none()

    def get_queryset(self):
        return UserAnalytics.objects.filter(user=self.request.user)