# Personal Diary Web Application

A feature-rich digital journaling platform that goes beyond simple text entries to provide a comprehensive self-reflection and personal growth tool.

## Distinctiveness and Complexity

This project stands apart from other web applications in several key ways:

### Innovative Features
- **Smart Emotion Tracking**: Unlike traditional diary applications that focus solely on text content, this project incorporates emoji-based mood tracking that allows users to express and monitor their emotional state over time. The implementation includes a sophisticated emoji picker with support for both predefined and custom emoji selections.

- **Intelligent Autosaving**: The application features a robust autosaving mechanism that preserves user content in real-time, preventing data loss and providing visual feedback through status indicators. This was implemented using asynchronous JavaScript and required careful handling of race conditions between manual saves and autosaves.

- **Rich Text Integration**: Rather than using basic text fields, the project integrates the Quill.js rich text editor with custom configurations and real-time word counting. This required careful integration between the frontend editor state and backend storage.

- **Goal Tracking System**: The application includes a sophisticated goal management system with support for subtasks, progress tracking, and deadline monitoring. Goals can be marked as complete/incomplete and include visual progress indicators.

### Technical Complexity
1. **State Management**: The application handles complex state management across multiple features:
   - Concurrent emoji selections with toggle functionality
   - Real-time tag management with dynamic updates
   - Autosaving state coordination with form submissions
   - Progress tracking for goals and subtasks

2. **Database Design**: The project uses a sophisticated data model with relationships between:
   - User profiles and preferences
   - Diary entries with rich text content
   - Tags and categorization
   - Goals and subtasks
   - Mood tracking entries

3. **Frontend Architecture**: The frontend implementation demonstrates complexity through:
   - Custom dark mode support with dynamic theme switching
   - Responsive design for mobile compatibility
   - Real-time content updates without page refreshes
   - Advanced DOM manipulation for dynamic content

## File Structure and Contents

### Backend (Python/Django)
- `models.py`: Defines the database schema for entries, goals, tags, and user profiles
- `views.py`: Contains view logic for handling entries, autosaving, and goal management
- `forms.py`: Form definitions for entry creation and user settings
- `urls.py`: URL routing configuration
- `api_views.py`: API endpoints for AJAX functionality
- `admin.py`: Admin interface customization

### Frontend (HTML/CSS/JavaScript)
- `templates/diary/`:
  - `layout.html`: Base template with navigation and theme support
  - `entry_form.html`: Rich text editor and tag management interface
  - `goals_list.html`: Goal tracking and management interface
  - `entry_detail.html`: Entry viewing with mood and tag display
  - `analytics.html`: Data visualization and insights

### Static Files
- `static/diary/css/style.css`: Custom styling and dark mode support
- `static/diary/js/`: JavaScript modules for various features

## Setup and Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Additional Notes

- The application uses SQLite by default but can be configured for PostgreSQL
- Dark mode preferences are persisted per user
- Rich text content is stored as HTML and sanitized on save
- Autosaves occur every 1000ms after content changes
- Goal progress is automatically calculated based on subtask completion

## Requirements

See `requirements.txt` for a complete list of dependencies. Key packages include:
- Django
- django-rest-framework
- bleach (for HTML sanitization)
- python-dateutil