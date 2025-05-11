from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'entries', api_views.DiaryEntryViewSet, basename='diary-entry')
router.register(r'goals', api_views.GoalViewSet, basename='goal')
router.register(r'wishlist', api_views.WishListItemViewSet, basename='wishlist-item')
router.register(r'letters', api_views.LetterViewSet, basename='letter')
router.register(r'analytics', api_views.UserAnalyticsViewSet, basename='user-analytics')

urlpatterns = [
    path('', include(router.urls)),
]