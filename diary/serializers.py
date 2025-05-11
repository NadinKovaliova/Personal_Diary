from rest_framework import serializers
from .models import DiaryEntry, Goal, WishListItem, Letter, UserAnalytics

class DiaryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryEntry
        fields = ['id', 'content', 'emoji_of_day', 'created_at', 'tags']
        read_only_fields = ['user']

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'title', 'description', 'deadline', 'progress', 'completed', 'subtasks', 'priority']
        read_only_fields = ['user']

class WishListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishListItem
        fields = ['id', 'title', 'description', 'price', 'purchased', 'priority']
        read_only_fields = ['user']

class LetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = ['id', 'content', 'delivery_date', 'written_date', 'status', 'notify_by_email']
        read_only_fields = ['user', 'written_date']

class UserAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnalytics
        fields = ['total_entries', 'writing_streaks', 'most_active_hour', 'mood_trends', 'last_entry_date']
        read_only_fields = ['user']