# GitHub Copilot Instructions

## Project Overview

**Mergington High School Activities API** - A FastAPI web application enabling students to browse and sign up for extracurricular activities. The project combines a Python backend (REST API) with a vanilla JavaScript frontend serving a simple activity management system.

### Architecture

- **Backend**: FastAPI application (`src/app.py`) providing two main endpoints for activity management
- **Frontend**: Static HTML/CSS/JS (`src/static/`) with real-time activity display and signup functionality
- **Data Model**: In-memory dictionary-based storage (no database) - data resets on server restart

## Key Files & Patterns

### Backend (`src/app.py`)

**Data Structure**: Activities stored as dict with activity name as key:
```python
activities = {
    "Activity Name": {
        "description": "...",
        "schedule": "...",
        "max_participants": int,
        "participants": [email1, email2, ...]
    }
}
```

**Endpoints**:
- `GET /activities` - Returns entire activities dict with participant lists
- `POST /activities/{activity_name}/signup?email=...` - Adds email to activity's participants list
- Validation: checks activity exists, student not already enrolled, capacity implicitly managed via participant count

**Key Pattern**: Email validation happens at frontend; backend uses email as student identifier (no separate users table).

### Frontend (`src/static/`)

**Workflow**:
1. Page loads → `fetchActivities()` calls `GET /activities`
2. Populates activity cards showing: name, description, schedule, spots left, current participants list
3. Form submission → `POST /signup` with email + activity name (URL-encoded)
4. Success/error message displayed for 5 seconds

**Important**: Query parameters for signup (not request body) - affects URL encoding in fetch calls.

## Development

### Running the Application

```bash
pip install fastapi uvicorn
python src/app.py
```

Open http://localhost:8000 or http://localhost:8000/static/index.html

API docs auto-generated at http://localhost:8000/docs

### Testing

Project uses pytest (configured in `pytest.ini` with `pythonpath = .`). Currently no test files exist - add as `src/test_*.py` or `test_*.py` following pytest conventions.

### Project Structure

```
src/
  app.py           # Main FastAPI application
  static/
    index.html     # Activity browser + signup form
    app.js         # Frontend logic
    styles.css     # Styling
```

## Important Conventions

1. **Activity Identifiers**: Use activity name (string) as unique key, not an ID - case-sensitive
2. **Email as Student ID**: No user registration; email serves as identifier for signup tracking
3. **Capacity Handling**: Validate `len(participants) < max_participants` before adding; no separate enrollment queue
4. **In-Memory Data**: All changes lost on restart - suitable for demo/learning only
5. **Static File Mounting**: FastAPI mounts `/static` directory; root `/` redirects to `index.html`

## Common Tasks

- **Add new activity**: Insert entry in `activities` dict in `app.py`
- **Add frontend feature**: Extend `fetchActivities()` or signup handler in `app.js`; call API endpoints via `/activities`
- **Modify API response**: Update dict structure - auto-reflected in FastAPI `/docs` schema
- **Handle form submission errors**: Check `response.ok` and extract `detail` field from error JSON

## Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- No database, authentication, or external APIs required
