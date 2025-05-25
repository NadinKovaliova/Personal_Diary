# Personal Diary Web Application

A feature-rich digital journaling platform that transforms the traditional diary-keeping experience into an interactive journey of self-reflection and personal growth.

### Demo video
https://youtu.be/JhY04nikgXM

## Distinctiveness and Complexity

This project demonstrates significant complexity through its integration of multiple advanced web technologies while maintaining a cohesive user experience focused on personal growth and emotional intelligence development.

1. **Complex Data Relationships**
   - This project implements intricate data models connecting entries, moods, goals, subtasks, and wishlist items
   - Features a sophisticated tag system
   - Implements soft delete patterns for trash and archive systems, beyond simple CRUD operations

2. **Advanced State Management**
   - Surpasses Mail project's basic inbox management with real-time autosaving and concurrent state handling
   - Implements complex goal tracking with hierarchical subtasks and progress calculations
   - Features drag-and-drop prioritization for wishlist items and goals

3. **Rich Text Integration**
   - Goes beyond basic text fields used in CS50W projects by integrating Quill.js editor
   - Implements custom toolbar configurations and real-time word counting
   - Handles HTML content sanitization and storage

4. **Psychological Elements**
   - Unique focus on emotional intelligence through mood tracking
   - Implements analytical tools for personal growth insights
   - Features goal progression visualization and achievement tracking


5. **Frontend Innovation**
   - Custom theme system with dark mode support
   - Real-time content updates without page refreshes
   - Complex DOM manipulation for dynamic content
   - Responsive design with mobile-first approach

6. **Backend Architecture**
   - Implements a comprehensive API system with token authentication
   - Features rate limiting and CORS support
   - Handles complex data relationships and cascading updates
   - Implements efficient database queries for analytics

7. **Advanced Features**
   - Intelligent autosaving with conflict resolution
   - Complex filtering and search across multiple models
   - Data visualization for mood trends and goal progress
   - Export functionality with CSV generation

### Why This Project Stands Out

While most diary applications focus solely on text storage, this project creates an interactive experience that helps users:

- **Smart Emotion Tracking**: Unlike traditional diary applications that focus solely on text content, this project incorporates emoji-based mood tracking that allows users to express and monitor their emotional state over time. 

- **Intelligent Autosaving**: The application features a robust autosaving mechanism that preserves user content in real-time, preventing data loss and providing visual feedback through status indicators. This was implemented using asynchronous JavaScript and required careful handling of race conditions between manual saves and autosaves.

- **Rich Text Integration**: Rather than using basic text fields, the project integrates the Quill.js rich text editor with custom configurations and real-time word counting. This required careful integration between the frontend editor state and backend storage.

- **Content Management System**: The application implements a sophisticated content management system with:
  - Archive functionality for preserving important entries
  - Trash system with soft delete and restoration capabilities
  - Custom wishlist feature for tracking personal desires and goals

- **Goal Tracking System**: The application includes a sophisticated goal management system with support for subtasks, progress tracking, and deadline monitoring. Goals can be marked as complete/incomplete and include visual progress indicators.


## File Structure and Contents

### Backend (Python/Django)
- `models.py`: Defines the database schema for entries, goals, tags, user profiles, wishlist items, archive, and trash
- `views.py`: Contains view logic for handling entries, autosaving, goal management, and content management
- `forms.py`: Form definitions for entry creation, user settings, and wishlist management
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
  - `entries_list.html`: Main entry management interface
  - `entries_archive.html`: Archive view with filtering
  - `trash.html`: Trash management with restoration
  - `wishlist.html`: Wishlist management interface

### API and Integration
- `api_views.py`: RESTful API endpoints
- `api_urls.py`: API routing configuration
- `serializers.py`: Complex data serialization

### Static Files
- `static/diary/css/style.css`: Custom styling and dark mode support

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

## Feature Details

### Entry Management
- **Rich Text Editor**
  - Quill.js integration with custom toolbar
  - Real-time word counting
  - Inline formatting tools
  - Table and list support
  - Autosaving with status indicators

- **Emotion Tracking**
  - Emoji-based mood selection
  - Mood trend analysis
  - Daily emotion picker
  - Emotion correlation insights

### Content Management System

#### Archive System
- Preserves archived entries in a separate view
- Maintains entry relationships and metadata
- Quick archive/unarchive functionality
- Search and filter capabilities
- Bulk archive operations support

#### Trash Management
- Entry restoration functionality
- Bulk restore/delete operations

#### Wishlist Feature
- Priority-based item organization
- Price tracking
- Purchase status tracking
- Item categorization
- Quick add functionality
- Edit functionality

### Goal Tracking System
- Hierarchical goal structure
- Subtask management
- Progress visualization on dashboard
- Deadline monitoring
- Priority levels
- Edit functionality

### Tag Management
- Custom tag creation
- Quick tag selection
- Tag statistics
- Tag search and filtering

### Analytics & Insights
- Writing patterns analysis
- Mood correlation reports
- Goal completion rates
- Tag usage statistics
- Activity heatmaps
- Progress tracking
- Data visualizations

### User Experience Features
- **Theme System**
  - Dark/light mode toggle
  - Persistence across sessions

- **Responsive Design**
  - Mobile-first approach
  - Touch-friendly interfaces
  - Adaptive layouts

- **Navigation**
  - Quick access menu
  - Search functionality


### Security Features
- User authentication
- Password policies
- Activity logging
- Data backup options
- Privacy controls

### Integration Features
- **API Access**
  - RESTful endpoints
  - Authentication tokens
  - Rate limiting
  - CORS support
  - Webhook integration

- **Export/Import**
  - CSV export

## Additional Notes

- The application uses SQLite by default but can be configured for PostgreSQL
- Dark mode preferences are persisted per user
- Rich text content is stored as HTML and sanitized on save
- Autosaves occur every 1000ms after content changes
- Goal progress is automatically calculated based on subtask completion
- Archive and trash systems use soft delete patterns
- Wishlist items support priority-based sorting and status tracking

## Requirements

See `requirements.txt` for a complete list of dependencies.