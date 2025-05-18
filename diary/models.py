from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dark_mode = models.BooleanField(default=False)
    font_preference = models.CharField(max_length=50, default='default')
    enable_2fa = models.BooleanField(default=False)
    


class DailyMood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    mood = models.CharField(max_length=50, blank=True)
    
    class Meta:
        unique_together = ['user', 'date']
        
    def __str__(self):
        return f"Mood for {self.user.username} on {self.date}"


class DiaryEntry(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('trash', 'Trash')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    emoji_of_day = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', blank=True)
    daily_mood = models.ForeignKey(
        DailyMood, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='entries'
    )
    is_autosave = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='active'
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Clean up old autosaves when saving a new entry
        if not self.is_autosave:
            DiaryEntry.objects.filter(
                user=self.user,
                is_autosave=True
            ).delete()
        # If this is a new entry or emoji has changed, update/create DailyMood
        if self.emoji_of_day:
            daily_mood, _ = DailyMood.objects.get_or_create(
                user=self.user,
                date=self.created_at.date(),
                defaults={'mood': self.emoji_of_day}
            )
            # Update existing mood instead of creating new one
            daily_mood.mood = self.emoji_of_day
            daily_mood.save()
            self.daily_mood = daily_mood
        super().save(*args, **kwargs)

    def move_to_trash(self):
        self.status = 'trash'
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        self.status = 'active'
        self.deleted_at = None
        self.save()
    
    def archive(self):
        self.status = 'archived'
        self.save()

    def __str__(self):
        return f"Entry by {self.user.username} on {self.created_at.date()}"


class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']

    def __str__(self):
        return self.name
    
    
class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)  # Make deadline optional
    progress = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    subtasks = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    order = models.IntegerField(default=0)
    
    def update_progress(self):
        if not self.subtasks:
            self.progress = 100 if self.completed else 0
            return
        completed = sum(1 for task in self.subtasks if task.get('completed', False))
        total = len(self.subtasks)
        self.progress = int((completed / total) * 100) if total > 0 else 0
        self.save()

    @property
    def is_overdue(self):
        return not self.completed and self.deadline < timezone.now().date()

    class Meta:
        ordering = [
            'completed', 
            models.F('deadline').asc(nulls_first=True),
            '-created_at'
        ]

    def __str__(self):
        return self.title


class WishListItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchased = models.BooleanField(default=False)
    priority = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
            ordering = [
                'purchased',
                models.F('priority').asc(nulls_first=True),  # Null priority first, then by priority
                '-created_at'
            ]


class Letter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    delivery_date = models.DateField()
    written_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[('pending', 'Pending'), ('delivered', 'Delivered')],
        default='pending'
    )
    notify_by_email = models.BooleanField(default=True)

class UserAnalytics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_entries = models.IntegerField(default=0)
    writing_streaks = models.IntegerField(default=0)
    most_active_hour = models.IntegerField(null=True)
    mood_trends = models.JSONField(default=dict)
    last_entry_date = models.DateField(null=True)