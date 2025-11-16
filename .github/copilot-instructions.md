# Library Project - AI Coding Instructions

## Project Overview
This is a Django 5.2 library management system (early development). The project follows standard Django structure with a single `shop` app managing book-related functionality. Configuration is in `library_conf/`, with SQLite for development.

## Architecture & Key Components

### Project Structure
- **`library_conf/`**: Django project settings and routing
  - `settings.py`: Database (SQLite), installed apps, middleware configuration
  - `urls.py`: Main URL router; currently only admin interface configured
  - `wsgi.py`, `asgi.py`: Application entry points

- **`shop/`**: Main Django app for library functionality
  - `models.py`: Data models (currently has `Book` model with title field)
  - `views.py`: View handlers (currently empty; views need implementation)
  - `admin.py`: Django admin registration (currently empty; models need registration)
  - `apps.py`: App configuration with `BigAutoField` as default PK
  - `tests.py`: Test suite (empty; add tests here)

### Database & Models
- Uses SQLite (`db.sqlite3`) via Django ORM
- Currently defines `Book` model in `shop/models.py` with:
  - `title`: CharField (max 100 chars, verbose name in Russian: "Названия книги")
- **Pattern**: Model field verbose names use Russian text—maintain this convention for international support
- Migrations auto-tracked in `shop/migrations/`; run `python manage.py migrate` after model changes

### Admin Configuration
- Django admin enabled at `/admin/` route
- Models registered in `shop/admin.py`; currently empty—**register Book model when implementing features**
- Example: `admin.site.register(Book, BookAdmin)` if customization needed

## Development Workflows

### Common Commands
```bash
# Run development server (localhost:8000)
python manage.py runserver

# Create/apply migrations after model changes
python manage.py makemigrations
python manage.py migrate

# Access admin interface
# Navigate to http://localhost:8000/admin/ with superuser credentials

# Create superuser for testing
python manage.py createsuperuser
```

### Testing
- Add tests in `shop/tests.py`
- Run via: `python manage.py test shop`
- Currently no test fixtures or custom test runners

## Project-Specific Patterns & Conventions

### Internationalization
- Settings: `LANGUAGE_CODE = 'en-us'`, `USE_I18N = True`
- **Convention**: Model field labels use Russian text (e.g., verbose_name in Cyrillic)
- When adding new fields, follow this pattern: use descriptive Russian names for user-facing labels

### URL Routing
- Main routes in `library_conf/urls.py`
- Use Django's `path()` function with view functions or class-based views
- Admin already routed; add shop-specific routes as needed (e.g., book list, book detail)

### Security Settings (Development)
- `DEBUG = True` (development only)
- `SECRET_KEY` hardcoded (unsafe for production—use environment variables)
- `ALLOWED_HOSTS = []` (restrict for production)
- These must be fixed before deployment

### App Registration
- `shop` app **not yet in `INSTALLED_APPS`** in settings.py
- Add `'shop'` to `INSTALLED_APPS` list in `library_conf/settings.py` before using models

## Integration Points & Dependencies

### Django 5.2 Specifics
- Default auto field is `BigAutoField` (modern best practice)
- Uses pathlib for BASE_DIR construction
- Standard middleware stack enabled (CSRF, Auth, Sessions)

### External Services
- No external APIs or services currently integrated
- Database: SQLite (file-based, no server needed for development)

### Cross-App Communication
- Single `shop` app; no inter-app imports needed yet
- Future: if additional apps added, import models via `from shop.models import Book`

## When Making Changes

1. **Adding Models**: Define in `shop/models.py`, follow existing `Book` model style (Russian verbose names)
2. **Registering Models**: Add to `shop/admin.py` for admin interface access
3. **Creating Views**: Add to `shop/views.py`, register routes in `library_conf/urls.py`
4. **Migrations**: Always run `makemigrations` → `migrate` sequence after model changes
5. **Testing**: Add tests in `shop/tests.py` before major feature commits
6. **Settings Changes**: Remember to add `'shop'` to `INSTALLED_APPS` if not already present
