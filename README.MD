# Personal Diary Web Application

A feature-rich digital journaling platform that transforms the traditional diary-keeping experience into an interactive journey of self-reflection and personal growth.

## Distinctiveness and Complexity

This project distinguishes itself from traditional web applications through its innovative approach to personal journaling and technical implementation. Unlike basic CRUD applications or simple blog platforms, this diary application creates a comprehensive ecosystem for personal growth and emotional intelligence development.

### Why This Project Stands Out

The application moves beyond standard diary implementations by integrating psychological concepts with modern web technologies. While most diary applications focus solely on text storage, this project creates an interactive experience that helps users:

- **Smart Emotion Tracking**: Unlike traditional diary applications that focus solely on text content, this project incorporates emoji-based mood tracking that allows users to express and monitor their emotional state over time. 

- **Intelligent Autosaving**: The application features a robust autosaving mechanism that preserves user content in real-time, preventing data loss and providing visual feedback through status indicators. This was implemented using asynchronous JavaScript and required careful handling of race conditions between manual saves and autosaves.

- **Rich Text Integration**: Rather than using basic text fields, the project integrates the Quill.js rich text editor with custom configurations and real-time word counting. This required careful integration between the frontend editor state and backend storage.

- **Content Management System**: The application implements a sophisticated content management system with:
  - Archive functionality for preserving important entries
  - Trash system with soft delete and restoration capabilities
  - Custom wishlist feature for tracking personal desires and goals

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
   - Wishlist items with priority system
   - Archive and trash status tracking

3. **Frontend Architecture**: The frontend implementation demonstrates complexity through:
   - Custom dark mode support with dynamic theme switching
   - Responsive design for mobile compatibility
   - Real-time content updates without page refreshes
   - Advanced DOM manipulation for dynamic content
   - Drag-and-drop wishlist prioritization
   - Interactive archive/trash management

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

### Goal Tracking System
- Hierarchical goal structure
- Subtask management
- Progress visualization on dashboard
- Deadline monitoring
- Priority levels

### Tag Management
- Custom tag creation
- Tag categorization
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