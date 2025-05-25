

import os
import django
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Ensure Django settings are configured
# Replace 'your_project_name.settings' with the actual path to your settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diary_app.settings')
django.setup()

# Import your models
from django.contrib.auth.models import User
from diary.models import ( # Replace 'app_name' with the actual name of your Django app
    Profile, DailyMood, DiaryEntry, Tag, Goal, WishListItem, Letter, UserAnalytics
)


def run():
    """
    Populates the database with demo data for the project.
    """
    print("Starting database seeding...")

    # --- Fetch existing users instead of creating new ones ---
    print("Fetching existing demo users...")
    try:
        admin_user = User.objects.get(username='admin')
        user1 = User.objects.get(username='NadinKovaliova')
        users = [admin_user, user1]
        print("Existing demo users fetched successfully.")
    except User.DoesNotExist:
        print("Error: One or more demo users ('admin', 'user1') do not exist.")
        print("Please create these users manually or run a previous version of the script that creates them.")
        return # Exit if users don't exist

    # --- Clear existing data for these users (optional, but good for a clean demo) ---
    #print("Clearing existing demo data for fetched users...")
    #Profile.objects.filter(user__in=users).delete()
    #DailyMood.objects.filter(user__in=users).delete()
    #DiaryEntry.objects.filter(user__in=users).delete()
    #Tag.objects.filter(user__in=users).delete()
    #Goal.objects.filter(user__in=users).delete()
# WishListItem.objects.filter(user__in=users).delete()
    #Letter.objects.filter(user__in=users).delete()
    #UserAnalytics.objects.filter(user__in=users).delete()
    #print("Existing demo data for fetched users cleared.")

    # A long string for diary entry content
    long_content = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    Curabitur pretium tincidunt lacus. Nulla gravida orci a odio. Nullam varius, turpis et commodo pharetra,
    est eros bibendum elit, nec luctus magna felis sollicitudin mauris. Integer in mauris eu nibh egestas dapibus.
    Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus.
    Donec id elit non mi porta gravida at eget metus. Nullam id dolor id nibh ultricies vehicula ut id elit.
    Cras justo odio, dapibus ac facilisis in, egestas eget quam. Vestibulum id ligula porta felis euismod semper.
    Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum.
    Felis euismod semper. Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum.
    Nullam quis risus eget urna mollis ornare vel eu leo. Cum sociis natoque penatibus et magnis dis parturient montes,
    nascetur ridiculus mus.
    """ * 5 # Repeat the content 5 times to make it significantly larger

    # --- Create Profiles ---
    print("Creating profiles...")
    for user in users:
        Profile.objects.get_or_create(
            user=user,
            defaults={
                'dark_mode': user.username == 'user1', # user1 has dark mode
            }
        )
    print("Profiles created.")

    # --- Create DailyMoods ---
    print("Creating daily moods...")
    today = timezone.now().date()
    DailyMood.objects.get_or_create(user=user1, date=today, defaults={'mood': 'happy'})
    DailyMood.objects.get_or_create(user=user1, date=today - timedelta(days=1), defaults={'mood': 'neutral'})
    DailyMood.objects.get_or_create(user=admin_user, date=today - timedelta(days=2), defaults={'mood': 'calm'})
    print("Daily moods created.")

    # --- Create Tags ---
    print("Creating tags...")
    tag_personal, _ = Tag.objects.get_or_create(user=user1, name='Personal')
    tag_work, _ = Tag.objects.get_or_create(user=user1, name='Work')
    tag_journal, _ = Tag.objects.get_or_create(user=admin_user, name='Journal')
    print("Tags created.")

    # --- Create DiaryEntries ---
    print("Creating diary entries with large content...")
    # Entry for user1, active
    entry1 = DiaryEntry.objects.create(
        user=user1,
        content=f"Today was a great day! I finished my project.\n\n{long_content}",
        emoji_of_day="�",
        created_at=timezone.now() - timedelta(hours=5),
        daily_mood=DailyMood.objects.get(user=user1, date=today)
    )
    entry1.tags.add(tag_personal, tag_work)

    # Entry for user1, archived
    entry2 = DiaryEntry.objects.create(
        user=user1,
        content=f"Reflecting on last week's challenges. Learned a lot.\n\n{long_content}",
        emoji_of_day="🤔",
        created_at=timezone.now() - timedelta(days=7),
        status='archived',
        daily_mood=DailyMood.objects.get(user=user1, date=today - timedelta(days=1))
    )
    entry2.tags.add(tag_personal)


    # Entry for admin_user, in trash
    entry4 = DiaryEntry.objects.create(
        user=admin_user,
        content=f"Old draft, moving to trash.\n\n{long_content}",
        emoji_of_day="🗑️",
        created_at=timezone.now() - timedelta(days=10),
        status='trash',
        deleted_at=timezone.now() - timedelta(days=1),
        daily_mood=DailyMood.objects.get(user=admin_user, date=today - timedelta(days=2))
    )
    entry4.tags.add(tag_journal)

    # Autosave entry for user1
    DiaryEntry.objects.create(
        user=user1,
        content=f"This is an autosaved draft with large content...\n\n{long_content}",
        is_autosave=True,
        created_at=timezone.now() - timedelta(minutes=10)
    )
    print("Diary entries created.")

    # --- Create Goals ---
    print("Creating goals...")
    Goal.objects.create(
        user=user1,
        title="Finish Django Project",
        description="Complete all features and deploy the application.",
        deadline=today + timedelta(days=30),
        progress=50,
        subtasks=[
            {'id': 1, 'text': 'Implement user authentication', 'completed': True},
            {'id': 2, 'text': 'Design database schema', 'completed': True},
            {'id': 3, 'text': 'Develop API endpoints', 'completed': False},
            {'id': 4, 'text': 'Write frontend components', 'completed': False}
        ],
        order=1
    )
    Goal.objects.create(
        user=user1,
        title="Read 'Clean Code'",
        description="Read the entire book by Robert C. Martin.",
        deadline=today + timedelta(days=15),
        completed=False,
        progress=20,
        subtasks=[
            {'id': 1, 'text': 'Read Chapter 1-3', 'completed': True},
            {'id': 2, 'text': 'Read Chapter 4-6', 'completed': False}
        ],
        order=2
    )
    
    Goal.objects.create(
        user=admin_user,
        title="Plan Q3 Strategy",
        description="Outline key objectives and initiatives for the third quarter.",
        deadline=today + timedelta(days=60),
        progress=0,
        subtasks=[],
        order=1
    )
    print("Goals created.")

    # --- Create WishListItems ---
    print("Creating wish list items...")
    WishListItem.objects.create(
        user=user1,
        title="New Mechanical Keyboard",
        description="Looking for a tactile switch keyboard.",
        price=150.00,
        purchased=False,
        priority=1
    )
    WishListItem.objects.create(
        user=user1,
        title="Noise-Cancelling Headphones",
        description="Sony WH-1000XM5",
        price=350.00,
        purchased=True
    )
    
    print("Wish list items created.")

    

    

    print("\nDatabase seeding complete!")
    print("Please ensure the following users exist in your database:")
    print("  username='admin_user'")
    print("  username='user1'")

if __name__ == '__main__':
    run()