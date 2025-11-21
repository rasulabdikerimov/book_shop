# Library Project - AI Coding Instructions

## Project Overview
This is a Django 5.2 library management system with an e-commerce platform. The `shop` app manages books, users, reviews, orders, payments, and deliveries. Configuration in `library_conf/`, SQLite for development.

## Architecture & Key Components

### Project Structure
- **`library_conf/`**: Django project settings and routing
  - `settings.py`: Custom user model (`CustomUser`), MEDIA/STATIC settings, i18n (Russian)
  - `urls.py`: Main router; includes shop URLs and MEDIA file serving
  - `wsgi.py`, `asgi.py`: Application entry points

- **`shop/`**: Main Django app with all models and views
  - `models.py`: 10+ models (CustomUser, Book, Order, Review, Payment, Delivery, etc.)
  - `views.py`: Homepage, book detail views (minimal; needs expansion)
  - `admin.py`: All models registered for admin interface
  - `urls.py`: Routes for homepage and book detail
  - `apps.py`: ShopConfig with `BigAutoField` as default PK
  - `tests.py`: Empty; add tests here

- **`templates/shop/`**: Template files
  - `homepage.html`: Lists books, genres, authors (uses `book.photo`, `author.photo`, `author.full_name`)
  - `book_detail.html`: Individual book page

- **`media/`**: User-uploaded files
  - `books/`, `authors/`, `users/`, `reviews/`, `employees/`: Image directories

### Core Models & Relationships

**User & Auth:**
- `CustomUser` (extends AbstractUser): email-based login, phone, address, profile photo
  - `USERNAME_FIELD = 'email'` (NOT username)
  - All models with ForeignKey to CustomUser cascade delete

**Book Catalog:**
- `Book`: Title, description, price, photo, pub_date (CharField, ГГГГ format)
  - ManyToMany: Genres, Languages, Authors
- `Genres`, `Languages`, `Countries`: Simple lookups with __str__ methods
- `Authors`: Full name, birth date, country FK, photo, biography

**Reviews & Engagement:**
- `Review`: User → Book, rating (stars), comment, timestamps
  - ManyToMany: ReviewImage
- `ReviewImage`: Images for reviews
- `Employee`: Can have ManyToMany Review (reverse from reviews)

**Orders & Commerce:**
- `Cart`: User → ManyToMany Books, quantity
- `Order`: User → ManyToMany Books, auto-generated 6-digit order_number, total_price
  - `order_number` generated on save via `random.randint(100000, 999999)`
- `Payment`: Order FK, payment_method, status ('В ожидании'), amount
- `Delivery`: Employee FK, Order FK, delivery_address, delivery_date (CharField), status

### Database & ORM
- SQLite (`db.sqlite3`) via Django ORM
- All verbose_names in Russian (Cyrillic) for i18n support
- Migrations in `shop/migrations/`; run `python manage.py migrate` after model changes
- `AUTH_USER_MODEL = 'shop.CustomUser'` set in settings.py

## Development Workflows

### Critical Setup Commands
```bash
# Apply migrations (MUST DO FIRST)
python manage.py migrate

# Create superuser for testing (uses email + username + phone + address)
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Create/apply new migrations
python manage.py makemigrations
python manage.py migrate
```

### Common Tasks
- **View models in admin**: `/admin/` (requires superuser)
- **Upload test images**: Via admin interface to book/author/user/review/employee fields
- **Add test data**: Use admin or create fixtures
- **Test views**: Visit `/` (homepage) or `/book/<id>/` (detail)

### Testing
- Add tests in `shop/tests.py`
- Run: `python manage.py test shop`

## Project-Specific Patterns & Conventions

### Internationalization (i18n)
- Settings: `LANGUAGE_CODE = 'ru-ru'`, `TIME_ZONE = 'Asia/Tashkent'`, `USE_I18N = True`
- **CRITICAL**: All model field `verbose_name` MUST be in Russian (Cyrillic)
- Example: `verbose_name='Названия книги:'` NOT `verbose_name='Book Title'`
- When adding fields, include Russian labels for admin UI

### Custom User Model
- Login via **email**, NOT username
- `USERNAME_FIELD = 'email'`
- `REQUIRED_FIELDS = ['username']` (for createsuperuser)
- Always import as: `from django.contrib.auth import get_user_model` or `from shop.models import CustomUser`
- Set `AUTH_USER_MODEL = 'shop.CustomUser'` in settings (already done)

### Image Handling
- `ImageField(upload_to='subdirectory/')` auto-creates media structure
- Template: `{{ object.field.url }}` to render image paths
- **Critical**: Check `MEDIA_URL` and `MEDIA_ROOT` in settings; already configured:
  ```python
  MEDIA_URL = 'media/'
  MEDIA_ROOT = BASE_DIR / 'media'
  ```
- URLs configured to serve media: `urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`

### Template Field Names
- Models use `photo` field, NOT `image`
- Models: `Authors.full_name`, NOT `name`
- Models: `Genres.genre`, `Languages.language`, `Countries.country`
- Always verify model field names match template references

### URL Routing
- Main app routes in `library_conf/urls.py`
- Shop app routes in `shop/urls.py`
- Use `path()` with view functions (not yet CBVs)
- Named routes: `'homepage'`, `'detail'` (book_id parameter)

### Security Settings (Development)
- `DEBUG = True` (dev only)
- `SECRET_KEY` hardcoded (use environment variables for production)
- `ALLOWED_HOSTS = []` (restrict for production)

### Admin Configuration
- All models registered in `shop/admin.py`
- All models have `__str__()` methods for readable admin display
- Order displays as: `Order #123456 - username`
- Review displays as: `Review by username for Book Title`

## Integration Points & Dependencies

### Django 5.2 Specifics
- Default auto field: `BigAutoField`
- Pathlib for BASE_DIR construction
- Standard middleware (CSRF, Auth, Sessions enabled)
- Template context processors: request, auth, messages

### External Services
- None currently integrated
- Database: SQLite (file-based, no server)

### Known Issues & Gotchas
1. **app not in INSTALLED_APPS**: Already fixed (shop is registered)
2. **CustomUser requires email authentication**: Remember `USERNAME_FIELD = 'email'`
3. **Order number collisions**: Generated randomly; very low collision risk with 6-digit range
4. **Image paths in templates**: Must use field names from models (photo, not image)
5. **Timestamps**: Use `auto_now_add` for created_at, `auto_now` for updated_at

## When Making Changes

1. **Adding New Models**:
   - Define in `shop/models.py` with Russian verbose_names
   - Use `__str__()` for readable display
   - Add ForeignKeys with `on_delete=models.CASCADE`

2. **Registering Models**:
   - Add to `shop/admin.py`: `admin.site.register(ModelName)`
   - Optionally create `ModelNameAdmin` class for field customization

3. **Creating/Modifying Views**:
   - Add to `shop/views.py`
   - Register routes in `shop/urls.py`
   - Pass context with QuerySets to templates

4. **Updating Templates**:
   - Verify field names match models (book.photo, NOT book.image)
   - Use `{{ field.url }}` for ImageField rendering
   - Reference many-to-many fields with `{% for item in field.all %}`

5. **Migrations Workflow**:
   - Always: `makemigrations` → `migrate` after model changes
   - Test locally with SQLite before deploying

6. **Testing Data**:
   - Use admin interface to upload images and test MEDIA serving
   - Create test fixtures for complex relationships (Books + Authors + Genres)

