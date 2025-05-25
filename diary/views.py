from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, ProfileSettingsForm
from django.contrib.auth.models import User
from .models import Profile, UserAnalytics, DiaryEntry, Goal, WishListItem, Letter, Tag, DailyMood
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
import json
from django.contrib.auth import login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.db import models, transaction
from django.db.models import Count, Avg
from django.db.models.functions import ExtractHour
import csv
from django.contrib.auth.hashers import check_password
from collections import Counter

MOOD_CATEGORIES = {
    'very_positive': ['🥰', '🤩', '😊', '😄', '🌟'],
    'positive': ['😌', '😎', '🙂', '😏'],
    'neutral': ['🤔', '😐', '😶', '😑'],
    'negative': ['😔', '😕', '😣', '😫'],
    'very_negative': ['😤', '😠', '😢', '😭', '💔']
}

def home(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'diary/home.html')

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile and analytics manually
            #Profile.objects.create(user=user)
            #UserAnalytics.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'diary/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'welcome_back')  # This is the key message
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'diary/login.html')

    
@login_required 
def dashboard(request):
    today = timezone.now().date()
    
    # Get today's mood
    today_mood = DailyMood.objects.filter(
        user=request.user,
        date=today
    ).first()

    # Get entries
    entries = DiaryEntry.objects.filter(user=request.user, status='active')
    
    # Calculate streaks
    dates = sorted(entries.values_list('created_at__date', flat=True))
    current_streak, max_streak = calculate_streak(dates)

    # Get latest insight
    latest_insight = None
    if current_streak >= 3:
        latest_insight = f"You're on a {current_streak}-day writing streak! 🔥"
    elif max_streak > current_streak:
        latest_insight = f"Your best streak was {max_streak} days! Can you beat it? ✨"
    elif entries.count() > 0:
        latest_insight = "Keep writing to build your streak! ✍️"

    context = {
        'recent_entries': entries.order_by('-created_at')[:3],
        'active_goals': Goal.objects.filter(user=request.user, completed=False).order_by('deadline')[:3],
        'wishlist_items': WishListItem.objects.filter(user=request.user, purchased=False).order_by('priority')[:3],
        'emoji_suggestions': ['🥰', '🤩', '😊', '😄', '🌟', '😌', '😎', '🙂', '😏', 
                            '🤔', '😐', '😑', '😔', '😕', '😣', '😫', '😤', '😠', '😢', '😭'],
        'today_mood': today_mood,
        'dark_mode': request.user.profile.dark_mode,
        'current_streak': current_streak,
        'max_streak': max_streak,
        'entries_this_month': entries.filter(created_at__month=timezone.now().month).count(),
        'latest_insight': latest_insight,
        'now': timezone.now()
    }
    return render(request, 'diary/dashboard.html', context)


@login_required
def entry_create(request):
    today = timezone.now().date()
    today_mood = DailyMood.objects.filter(
        user=request.user,
        date=today
    ).first()

    if request.method == 'POST':
        content = request.POST.get('content')
        emoji = request.POST.get('emoji')
        tag_ids = request.POST.get('tags').split(',') 
        

        try:
            current_date = timezone.now()
        except AttributeError:
            current_date = datetime.now()

        # Create or update daily mood first
        if emoji:
            daily_mood, _ = DailyMood.objects.get_or_create(
                user=request.user,
                date=current_date.date(),
                defaults={'mood': emoji}
            )
            # Update mood if it exists
            if not _:  # if mood already existed
                daily_mood.mood = emoji
                daily_mood.save()
        else:
            daily_mood = None

        # Create entry with the daily mood reference
        entry = DiaryEntry.objects.create(
            user=request.user,
            content=content,
            emoji_of_day=emoji,
            created_at=current_date,
            daily_mood=daily_mood
        )

        # Add selected tags to the entry
        if tag_ids and tag_ids[0]:  # Check if there are any tags
            tags = Tag.objects.filter(id__in=tag_ids, user=request.user)
            entry.tags.add(*tags)
        
        # Update analytics
        analytics = UserAnalytics.objects.get(user=request.user)
        analytics.total_entries += 1
        analytics.last_entry_date = current_date.date()
        analytics.save()
        
        return redirect('entry-detail', pk=entry.pk)

    context = {
        'emoji_suggestions': ['🥰', '🤩', '😊', '😄', '🌟', '😌', '😎', '🙂', '😏', 
                              '🤔', '😐', '😑', '😔', '😕', '😣', '😫', '😤', '😠', '😢', '😭'],
        'user_tags': Tag.objects.filter(user=request.user),
        'dark_mode': request.user.profile.dark_mode,
        'today_mood': today_mood,  # Add today's mood to context
        'is_new_entry': True  # Add this flag
    }
    return render(request, 'diary/entry_form.html', context)

@login_required
def entry_detail(request, pk):
    entry = get_object_or_404(DiaryEntry.objects.prefetch_related('tags'), pk=pk, user=request.user)
    # Determine view type based on entry status
    view_type = 'trash' if entry.status == 'trash' else 'archive' if entry.status == 'archived' else 'active'
    return render(request, 'diary/entry_detail.html', {
        'entry': entry,
        'view_type': view_type,
        'dark_mode': request.user.profile.dark_mode
        })


@login_required
def entry_edit(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.content = request.POST.get('content')
        entry.emoji_of_day = request.POST.get('emoji')
        tag_ids = request.POST.get('tags').split(',') if request.POST.get('tags') else []
        
        # Clear existing tags and add new ones
        entry.tags.clear()
        if tag_ids:
            entry.tags.add(*Tag.objects.filter(id__in=tag_ids, user=request.user))
            
        entry.save()
        return redirect('entry-detail', pk=entry.pk)
    
    context = {
        'entry': entry,
        'emoji_suggestions': ['🥰', '🤩', '😊', '😄', '🌟', '😌', '😎', '🙂', '😏', 
                              '🤔', '😐', '😑', '😔', '😕', '😣', '😫', '😤', '😠', '😢', '😭'],
        'user_tags': Tag.objects.filter(user=request.user),
        'dark_mode': request.user.profile.dark_mode,
        'selected_tags': [str(tag.id) for tag in entry.tags.all()],
        'is_new_entry': False 
    }
    return render(request, 'diary/entry_form.html', context)

@login_required
@require_POST 
def entry_autosave(request):
    data = json.loads(request.body)
    entry_id = data.get('entry_id')
    content = data.get('content')
    emoji = data.get('emoji', '')
    tags = data.get('tags', '')
    
    try:
        if entry_id and entry_id.strip():
            # Update existing entry
            entry = get_object_or_404(DiaryEntry, pk=entry_id, user=request.user)
            entry.content = content
            entry.emoji_of_day = emoji
            entry.save(update_fields=['content', 'emoji_of_day'])
            
            # Update tags if provided
            if tags:
                tag_ids = tags.split(',')
                entry.tags.clear()
                entry.tags.add(*Tag.objects.filter(id__in=tag_ids, user=request.user))
        else:
            # Create temporary autosave entry
            entry = DiaryEntry.objects.create(
                user=request.user,
                content=content,
                emoji_of_day=emoji,
                is_autosave=True  # Add this field to your DiaryEntry model
            )
            
            # Add tags if provided 
            if tags:
                tag_ids = tags.split(',')
                entry.tags.add(*Tag.objects.filter(id__in=tag_ids, user=request.user))

        return JsonResponse({
            'success': True, 
            'entry_id': entry.id,
            'message': 'Entry saved'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_POST
def tag_create(request):
    name = request.POST.get('name').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'Tag name is required'})
    
    tag, created = Tag.objects.get_or_create(
        user=request.user,
        name=name
    )
    
    return JsonResponse({
        'success': True,
        'tag': {
            'id': tag.id,
            'name': tag.name
        }
    })

@login_required
@require_POST
def tag_delete(request, tag_id):
    try:
        tag = get_object_or_404(Tag, id=tag_id, user=request.user)
        
        # Check if tag is used in any entries
        entry_count = tag.diaryentry_set.count()
        
        if entry_count > 0:
            # Remove tag from all entries but keep the entries
            tag.diaryentry_set.clear()
        
        # Delete the tag itself
        tag.delete()
        
        messages.success(request, f'Tag "{tag.name}" has been deleted.')
        return JsonResponse({
            'success': True,
            'wasUsed': entry_count > 0
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)

@require_POST
@login_required
def toggle_dark_mode(request):
    profile = request.user.profile
    profile.dark_mode = not profile.dark_mode
    profile.save()
    return JsonResponse({'success': True, 'dark_mode': profile.dark_mode})


@login_required
@require_POST
def update_mood(request):
    data = json.loads(request.body)
    mood = data.get('mood', '')
    date = data.get('date') or timezone.now().date()
    
    # Update or create the daily mood
    daily_mood, created = DailyMood.objects.update_or_create(
        user=request.user,
        date=date,
        defaults={'mood': mood}
    )
    
    # Update associated diary entry if it exists
    entry = DiaryEntry.objects.filter(
        user=request.user,
        created_at__date=date
    ).first()
    
    if entry:
        entry.emoji_of_day = mood
        entry.daily_mood = daily_mood
        entry.save(update_fields=['emoji_of_day', 'daily_mood'])
    
    # Update UserAnalytics mood trends
    analytics = request.user.useranalytics
    mood_trends = analytics.mood_trends or {}
    
    if mood:
        current_month = date.strftime('%Y-%m')
        if current_month not in mood_trends:
            mood_trends[current_month] = {}
        mood_trends[current_month][str(date)] = mood
    
    analytics.mood_trends = mood_trends
    analytics.save()

    return JsonResponse({
        'success': True,
        'mood': mood,
        'date': str(date)
    })

@login_required
def entries_list(request):
    view_type = request.GET.get('view_type', 'active')
    entries = DiaryEntry.objects.filter(user=request.user).prefetch_related('tags')
    
    # Base query depending on view type
    if view_type == 'trash':
        entries = DiaryEntry.objects.filter(user=request.user, status='trash')
    elif view_type == 'archive':
        entries = DiaryEntry.objects.filter(user=request.user, status='archived')
    else:
        entries = DiaryEntry.objects.filter(user=request.user, status='active')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        entries = entries.filter(
            Q(content__icontains=search_query) | 
            Q(tags__name__icontains=search_query)
        ).distinct()

    # Date filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        entries = entries.filter(created_at__gte=date_from)
    if date_to:
        entries = entries.filter(created_at__lte=date_to)

    # Tag filtering
    selected_tags = request.GET.getlist('tags')
    if selected_tags:
        entries = entries.filter(tags__id__in=selected_tags).distinct()

    # Sorting
    sort = request.GET.get('sort', '-created_at')
    entries = entries.order_by(sort)

    # Add pagination
    paginator = Paginator(entries, 10)  # Show 10 entries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'entries': page_obj, 
        'view_type': view_type,
        'search_query': search_query,
        'sort': sort,
        'selected_tags': selected_tags,
        'all_tags': Tag.objects.filter(user=request.user),
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'diary/entries_list.html', context)

@login_required
@require_POST
def entry_trash(request, pk):
    try:
        entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
        entry.status = 'trash'
        entry.deleted_at = timezone.now()
        entry.save()
        messages.success(request, 'Entry moved to trash successfully.')
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def entry_restore(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    entry.restore()
    messages.success(request, 'Entry restored.')
    return JsonResponse({'success': True})

@login_required
@require_POST
def entry_archive(request, pk):
    try:
        entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
        entry.status = 'archived'
        entry.save()
        messages.success(request, 'Entry archived successfully.')
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def entries_trash(request):
    # Base query for trashed entries
    entries = DiaryEntry.objects.filter(user=request.user, status='trash')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        entries = entries.filter(
            Q(content__icontains=search_query) | 
            Q(tags__name__icontains=search_query)
        ).distinct()

    # Date filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        entries = entries.filter(created_at__gte=date_from)
    if date_to:
        entries = entries.filter(created_at__lte=date_to)

    # Tag filtering
    selected_tags = request.GET.getlist('tags')
    if selected_tags:
        entries = entries.filter(tags__id__in=selected_tags)

    # Sorting
    sort = request.GET.get('sort', '-created_at')
    entries = entries.order_by(sort)
    
    # Add pagination
    paginator = Paginator(entries, 10)  # Show 10 entries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'entries': page_obj,
        'view_type': 'trash',
        'search_query': search_query,
        'sort': sort,
        'selected_tags': selected_tags,
        'all_tags': Tag.objects.filter(user=request.user),
        'date_from': date_from,
        'date_to': date_to,
        'dark_mode': request.user.profile.dark_mode
    }
    
    return render(request, 'diary/entries_list.html', context)

@login_required
def entries_archive(request):
    # Base query for archived entries
    entries = DiaryEntry.objects.filter(user=request.user, status='archived')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        entries = entries.filter(
            Q(content__icontains=search_query) | 
            Q(tags__name__icontains=search_query)
        ).distinct()

    # Date filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        entries = entries.filter(created_at__gte=date_from)
    if date_to:
        entries = entries.filter(created_at__lte=date_to)

    # Tag filtering
    selected_tags = request.GET.getlist('tags')
    if selected_tags:
        entries = entries.filter(tags__id__in=selected_tags)

    # Sorting
    sort = request.GET.get('sort', '-created_at')
    entries = entries.order_by(sort)
    
    # Add pagination
    paginator = Paginator(entries, 10)  # Show 10 entries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'entries': page_obj,
        'view_type': 'archive',
        'search_query': search_query,
        'sort': sort,
        'selected_tags': selected_tags,
        'all_tags': Tag.objects.filter(user=request.user),
        'date_from': date_from,
        'date_to': date_to,
        'dark_mode': request.user.profile.dark_mode
    }
    
    return render(request, 'diary/entries_list.html', context)

@login_required
@require_POST
def entry_unarchive(request, pk):
    try:
        entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
        entry.status = 'active'
        entry.save()
        messages.success(request, 'Entry unarchived successfully.')
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def entry_permanent_delete(request, pk):
    try:
        entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user, status='trash')
        entry.delete()
        messages.success(request, 'Entry permanently deleted.')
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def logout_view(request):
    """Handle logout for both GET and POST requests"""
    auth_logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def goals_list(request):
    goals = Goal.objects.filter(user=request.user)
    
    sort = request.GET.get('sort', 'custom')

    overdue_goals = goals.filter(
        completed=False,
        deadline__lt=timezone.now().date()
    )
    
    if overdue_goals.exists():
        messages.warning(request, f'You have {overdue_goals.count()} overdue goals!')

    if sort == 'date_asc':
        goals = goals.order_by('created_at')
    elif sort == 'date_desc':
        goals = goals.order_by('-created_at')
    elif sort == 'deadline_asc':
        goals = goals.order_by(models.F('deadline').asc(nulls_last=True))
    elif sort == 'deadline_desc':
        goals = goals.order_by(models.F('deadline').desc(nulls_last=True))
    else:
        # Default custom order
        goals = goals.order_by('order', 'completed', '-created_at')
    
    return render(request, 'diary/goals_list.html', {
        'goals': goals,
        'dark_mode': request.user.profile.dark_mode,
        'current_sort': sort
    })
@login_required
@require_POST
def reorder_goals(request):
    try:
        order_data = json.loads(request.body)
        goals = order_data.get('goals', [])
        
        with transaction.atomic():
            for index, goal_id in enumerate(goals):
                Goal.objects.filter(
                    id=goal_id, 
                    user=request.user
                ).update(order=index)
                
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def goal_create(request):
    data = json.loads(request.body)
    title = data.get('title')
    description = data.get('description', '')
    deadline = data.get('deadline') or None
    subtasks = data.get('subtasks', [])
    
    if title:
        goal = Goal.objects.create(
            user=request.user,
            title=title,
            description=description,
            deadline=deadline,
            subtasks=[{'title': task, 'completed': False} for task in subtasks]
        )
        goal.update_progress()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
@require_POST
def goal_edit(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    data = json.loads(request.body)
    
    try:
        goal.title = data.get('title', goal.title)
        goal.description = data.get('description', goal.description)
        goal.deadline = data.get('deadline') or None
        
        # Update subtasks if provided
        if 'subtasks' in data:
            goal.subtasks = data['subtasks']
            
        goal.save()
        goal.update_progress()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def toggle_goal_completed(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.completed = not goal.completed
    goal.save()
    goal.update_progress()
    return JsonResponse({'success': True, 'completed': goal.completed})

@login_required
@require_POST
def toggle_subtask(request, goal_id, index):
    goal = get_object_or_404(Goal, pk=goal_id, user=request.user)
    subtasks = goal.subtasks
    
    if 0 <= index < len(subtasks):
        subtasks[index]['completed'] = not subtasks[index]['completed']
        goal.subtasks = subtasks
        goal.save()
        goal.update_progress()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=404)

@login_required
@require_POST
def add_subtask(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id, user=request.user)
    data = json.loads(request.body)
    title = data.get('title')
    
    if title:
        subtasks = goal.subtasks or []
        subtasks.append({
            'title': title,
            'completed': False
        })
        goal.subtasks = subtasks
        goal.save()
        goal.update_progress()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
@require_POST
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.delete()
    return JsonResponse({'success': True})

@login_required
def wishlist(request):
    wishlist_items = WishListItem.objects.filter(user=request.user)
    
    # Get sort parameter
    sort = request.GET.get('sort', 'custom')
    
    if sort == 'date_asc':
        wishlist_items = wishlist_items.order_by('created_at')
    elif sort == 'date_desc':
        wishlist_items = wishlist_items.order_by('-created_at')
    elif sort == 'price_asc':
        wishlist_items = wishlist_items.order_by(models.F('price').asc(nulls_last=True))
    elif sort == 'price_desc':
        wishlist_items = wishlist_items.order_by(models.F('price').desc(nulls_last=True))
    elif sort == 'priority_asc':
        wishlist_items = wishlist_items.order_by(models.F('priority').asc(nulls_last=True))
    elif sort == 'priority_desc':
        wishlist_items = wishlist_items.order_by(models.F('priority').desc(nulls_last=True))
    else:
        # Default custom order
        wishlist_items = wishlist_items.order_by('purchased', '-priority', '-created_at')
    
    context = {
        'wishlist_items': wishlist_items,
        'dark_mode': request.user.profile.dark_mode,
        'current_sort': sort
    }
    return render(request, 'diary/wishlist.html', context)

@login_required
@require_POST
def toggle_wishlist_purchased(request, pk):
    item = get_object_or_404(WishListItem, pk=pk, user=request.user)
    item.purchased = not item.purchased
    item.save()
    return JsonResponse({'success': True, 'purchased': item.purchased})

@login_required
@require_POST
def quick_add_goal(request):
    data = json.loads(request.body)
    title = data.get('title')
    
    if title:
        Goal.objects.create(
            user=request.user,
            title=title
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
@require_POST
def quick_add_wishlist(request):
    data = json.loads(request.body)
    title = data.get('title')
    description = data.get('description', '')
    price = data.get('price')
    purchased = data.get('purchased', False)
    priority = data.get('priority', 0)
    if title:
        try:
            price = float(price) if price else None
        except ValueError:
            price = None
            
        WishListItem.objects.create(
            user=request.user,
            title=title,
            description=description,
            price=price,
            purchased=purchased,
            priority=priority
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
@require_POST
def delete_wishlist_item(request, pk):
    item = get_object_or_404(WishListItem, pk=pk, user=request.user)
    item.delete()
    return JsonResponse({'success': True})

@login_required
@require_POST
def reorder_wishlist(request):
    try:
        order_data = json.loads(request.body)
        items = order_data.get('items', [])
        
        with transaction.atomic():
            for index, item_id in enumerate(items):
                WishListItem.objects.filter(
                    id=item_id, 
                    user=request.user
                ).update(priority=len(items) - index)
                
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
@login_required
@require_POST
def wishlist_edit(request, pk):
    item = get_object_or_404(WishListItem, pk=pk, user=request.user)
    data = json.loads(request.body)
    
    try:
        item.title = data.get('title', item.title)
        item.description = data.get('description', item.description)
        
        price = data.get('price')
        if price:
            try:
                item.price = float(price)
            except ValueError:
                item.price = None
        
        item.priority = data.get('priority', item.priority)
        item.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            # Save profile changes
            profile = form.save(commit=False)
            
            # Update email
            request.user.email = form.cleaned_data['email']
            request.user.save()
            
            # Handle password change
            if form.cleaned_data['new_password']:
                if check_password(form.cleaned_data['current_password'], request.user.password):
                    request.user.set_password(form.cleaned_data['new_password'])
                    request.user.save()
                    messages.success(request, 'Password updated successfully')
                else:
                    messages.error(request, 'Current password is incorrect')
            
            profile.save()
            messages.success(request, 'Settings updated successfully')
            return redirect('profile-settings')
    else:
        form = ProfileSettingsForm(instance=request.user.profile)

    return render(request, 'diary/profile_settings.html', {
        'form': form,
        'dark_mode': request.user.profile.dark_mode
    })

@login_required
def export_entries(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="diary_entries.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Content', 'Mood', 'Tags'])
    
    entries = DiaryEntry.objects.filter(user=request.user)
    for entry in entries:
        writer.writerow([
            entry.created_at.strftime('%Y-%m-%d'),
            entry.content,
            entry.emoji_of_day,
            ', '.join(tag.name for tag in entry.tags.all())
        ])
    
    return response

@login_required
def analytics_view(request):
    # Get user's entries
    entries = DiaryEntry.objects.filter(user=request.user, status='active')
    
    # Basic statistics
    total_entries = entries.count()
    entries_this_month = entries.filter(
        created_at__month=timezone.now().month
    ).count()
    
    # Calculate average words per entry
    def count_words(content):
        return len(content.split())
    
    avg_words = round(sum(count_words(entry.content) for entry in entries) / total_entries) if total_entries > 0 else 0
    
    # Calculate streaks
    dates = sorted(entries.values_list('created_at__date', flat=True))
    current_streak, max_streak = calculate_streak(dates)
    
    # Use the constant for mood categories
    mood_categories = MOOD_CATEGORIES

    # Mood trends data
    moods = DailyMood.objects.filter(user=request.user).order_by('date')
    mood_dates = [mood.date.strftime('%Y-%m-%d') for mood in moods]
    
    # Convert moods to numerical values for the chart
    mood_data = []
    mood_emojis = []  # Store actual emojis for display
    
    for mood in moods:
        if any(mood.mood in emojis for emojis in mood_categories['very_positive']):
            mood_data.append(2)
            mood_emojis.append(mood.mood)
        elif any(mood.mood in emojis for emojis in mood_categories['positive']):
            mood_data.append(1)
            mood_emojis.append(mood.mood)
        elif any(mood.mood in emojis for emojis in mood_categories['neutral']):
            mood_data.append(0)
            mood_emojis.append(mood.mood)
        elif any(mood.mood in emojis for emojis in mood_categories['negative']):
            mood_data.append(-1)
            mood_emojis.append(mood.mood)
        elif any(mood.mood in emojis for emojis in mood_categories['very_negative']):
            mood_data.append(-2)
            mood_emojis.append(mood.mood)
        else:
            mood_data.append(0)
            mood_emojis.append('😐')

    # Calendar view data
    selected_month = request.GET.get('month', timezone.now().month)
    selected_year = request.GET.get('year', timezone.now().year)
    
    # Get all moods for selected month
    month_moods = DailyMood.objects.filter(
        user=request.user,
        date__year=selected_year,
        date__month=selected_month
    ).values('date', 'mood')
    
    # Create calendar data
    calendar_data = {}
    for mood in month_moods:
        calendar_data[mood['date'].strftime('%Y-%m-%d')] = {
            'emoji': mood['mood'],
            'mood_class': get_mood_class(mood['mood'], mood_categories)
        }

    # Year mood view data
    selected_year = request.GET.get('year', timezone.now().year)
    year_moods = DailyMood.objects.filter(
        user=request.user,
        date__year=selected_year
    ).values('date', 'mood')

    # Get all entries for the year
    year_entries = DiaryEntry.objects.filter(
        user=request.user,
        created_at__year=selected_year,
        status='active'
    ).values('created_at__date', 'id')

    # Create entries dictionary by date
    entries_by_date = {}
    for entry in year_entries:
        date_str = entry['created_at__date'].strftime('%Y-%m-%d')
        if date_str not in entries_by_date:
            entries_by_date[date_str] = []
        entries_by_date[date_str].append(entry['id'])

    # Create year mood data structure (by months)
    year_mood_data = {}
    for i in range(1, 13):
        year_mood_data[i] = {
            'moods': [],
            'stats': {
                'mood-very-positive': 0,
                'mood-positive': 0,
                'mood-neutral': 0,
                'mood-negative': 0,
                'mood-very-negative': 0
            }
        }
    
    for mood in year_moods:
        month = mood['date'].month
        date_str = mood['date'].strftime('%Y-%m-%d')
        mood_class = get_mood_class(mood['mood'], mood_categories)
        
        entry_data = {
            'day': mood['date'].day,
            'emoji': mood['mood'],
            'mood_class': mood_class,
            'date': date_str,
            'entries': entries_by_date.get(date_str, [])
        }
        
        year_mood_data[month]['moods'].append(entry_data)
        if mood_class:
            year_mood_data[month]['stats'][mood_class] += 1

    # Writing activity by hour
    activity_hours = list(range(24))
    hour_counts = entries.annotate(
        hour=ExtractHour('created_at')
    ).values('hour').annotate(count=Count('id'))
    
    activity_data = [0] * 24
    for item in hour_counts:
        activity_data[item['hour']] = item['count']
    
    # Tag analysis
    tag_usage = entries.values('tags__name').annotate(
        count=Count('id')
    ).exclude(tags__name=None).order_by('-count')[:5]
    
    tag_labels = [item['tags__name'] for item in tag_usage]
    tag_data = [item['count'] for item in tag_usage]
    
    # Generate insights
    insights = []
    
    # Most active hour
    most_active_hour = activity_hours[activity_data.index(max(activity_data))]
    insights.append(f"You're most productive at {most_active_hour:02d}:00!")
    
    # Mood insight
    if mood_data:
        positive_moods = sum(1 for m in mood_data if m > 0)
        very_positive_moods = sum(1 for m in mood_data if m == 2)
        
        if very_positive_moods / len(mood_data) > 0.5:
            insights.append("You've been in an amazing mood lately! 🤩✨")
        elif positive_moods / len(mood_data) > 0.6:
            insights.append("You've been maintaining a positive outlook! 😊")
        elif sum(1 for m in mood_data if m < 0) / len(mood_data) > 0.7:
            insights.append("Things have been tough lately. Remember to take care of yourself 💝")
    
    # Writing consistency
    if current_streak > 0:
        insights.append(f"Current writing streak: {current_streak} days 🔥")
    if max_streak > current_streak:
        insights.append(f"Best writing streak: {max_streak} days ⭐")
    
    context = {
        'total_entries': total_entries,
        'current_streak': current_streak,
        'max_streak': max_streak,
        'avg_words': avg_words,
        'entries_this_month': entries_this_month,
        'mood_dates': json.dumps(mood_dates),
        'mood_data': json.dumps(mood_data),
        'mood_emojis': json.dumps(mood_emojis),
        'activity_hours': json.dumps(activity_hours),
        'activity_data': json.dumps(activity_data),
        'tag_labels': json.dumps(tag_labels),
        'tag_data': json.dumps(tag_data),
        'insights': insights,
        'calendar_data': json.dumps(calendar_data),
        'selected_month': int(selected_month),
        'selected_year': int(selected_year),
        'months': [
            {'number': i, 'name': timezone.datetime(2000, i, 1).strftime('%B')} 
            for i in range(1, 13)
        ],
        'year_mood_data': json.dumps(year_mood_data),
        'selected_year': int(selected_year),
        'available_years': sorted(set(
            DailyMood.objects.filter(user=request.user)
            .dates('date', 'year')
            .values_list('date__year', flat=True)
        ))
    }
    
    return render(request, 'diary/analytics.html', context)

@login_required
def get_year_moods(request, year):
    year_moods = DailyMood.objects.filter(
        user=request.user,
        date__year=year
    ).values('date', 'mood')
    
    # Use the constant for mood categories
    mood_categories = MOOD_CATEGORIES
    
    # Create year mood data structure
    year_mood_data = {}
    for i in range(1, 13):
        year_mood_data[i] = {
            'moods': [],
            'stats': {
                'mood-very-positive': 0,
                'mood-positive': 0,
                'mood-neutral': 0,
                'mood-negative': 0,
                'mood-very-negative': 0
            }
        }
    
    for mood in year_moods:
        month = mood['date'].month
        mood_class = get_mood_class(mood['mood'], mood_categories)
        year_mood_data[month]['moods'].append({
            'day': mood['date'].day,
            'emoji': mood['mood'],
            'mood_class': mood_class
        })
        if mood_class:
            year_mood_data[month]['stats'][mood_class] += 1
    
    return JsonResponse(year_mood_data)

def get_mood_class(emoji, mood_categories):
    """Helper function to determine CSS class based on mood"""
    if any(emoji in emojis for emojis in mood_categories['very_positive']):
        return 'mood-very-positive'
    elif any(emoji in emojis for emojis in mood_categories['positive']):
        return 'mood-positive'
    elif any(emoji in emojis for emojis in mood_categories['neutral']):
        return 'mood-neutral'
    elif any(emoji in emojis for emojis in mood_categories['negative']):
        return 'mood-negative'
    elif any(emoji in emojis for emojis in mood_categories['very_negative']):
        return 'mood-very-negative'
    return ''

@login_required
@require_POST
def bulk_operation(request, operation):
    data = json.loads(request.body)
    entry_ids = data.get('entry_ids', [])
    
    if not entry_ids:
        return JsonResponse({'success': False, 'error': 'No entries selected'})
    
    try:
        entries = DiaryEntry.objects.filter(
            user=request.user,
            id__in=entry_ids
        )
        
        if operation == 'archive':
            entries.update(status='archived')
            msg = f"{len(entry_ids)} entries archived successfully"
        
        elif operation == 'unarchive':
            entries.update(status='active')
            msg = f"{len(entry_ids)} entries unarchived successfully"
        
        elif operation == 'restore':
            entries.update(status='active', deleted_at=None)
            msg = f"{len(entry_ids)} entries restored successfully"
        
        elif operation == 'delete':
            entries.filter(status='trash').delete()
            msg = f"{len(entry_ids)} entries deleted permanently"
            
        elif operation == 'trash':  # Add this new condition
            entries.update(status='trash', deleted_at=timezone.now())
            msg = f"{len(entry_ids)} entries moved to trash successfully"
        
        messages.success(request, msg)
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def calculate_streak(dates):
    if not dates:
        return 0, 0
        
    # Sort dates in ascending order
    dates = sorted(dates)
    today = timezone.now().date()
    
    current_streak = 1
    max_streak = 1
    
    # Initialize counters
    for i in range(1, len(dates)):
        # Calculate difference between consecutive dates
        date_diff = (dates[i] - dates[i-1]).days
        
        if date_diff == 1:
            # Increment streak for consecutive days
            current_streak += 1
            # Update max streak if current is higher
            max_streak = max(max_streak, current_streak)
        elif date_diff > 1:
            # Reset streak counter when there's a gap
            current_streak = 1
    
    # Check if the streak is still active (includes today)
    if dates[-1] != today:
        current_streak = 0
    
    return current_streak, max_streak


