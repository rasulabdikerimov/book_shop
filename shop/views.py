
from django.shortcuts import redirect, render,get_object_or_404
from .models import Book, Genres, Authors, Languages, Countries, Review, ReviewImage, CustomUser
# Create your views here.
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, ReviewForm,CustomUserChangeForm
from django.contrib.auth import login,authenticate,logout
from django.http import JsonResponse
def homepage(request):
    books = Book.objects.all()[:4]
    genres = Genres.objects.all()[:6]
    authors = Authors.objects.all()[:6]
    context = {
        'books': books,
        'genres': genres,
        'authors': authors,
    }
    return render(request, 'shop/homepage.html', context)

def popular_books(request):
    books_list = Book.objects.all()
    paginator = Paginator(books_list, 8)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    context = {
        'books': books,
    }
    return render(request, 'shop/popular_books.html', context)


def search_results(request):
    query = request.GET.get('q', '')
    books_list = Book.objects.filter(
        Q(title__icontains=query)|
        Q(authors__full_name__icontains=query)
        ).distinct()
    
    paginator = Paginator(books_list, 8)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    context = {
        'books': books,
        'query': query,
    }
    return render(request, 'shop/search_results.html', context)
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = Review.objects.filter(book=book).select_related('user')
    related_books = Book.objects.filter(genres__in=book.genres.all()).exclude(id=book_id).distinct()[:4]

    review_form = ReviewForm()
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
            
        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.book = book
            new_review.user = request.user
            new_review.save()
            
            # Обработка загруженных изображений
            for img in request.FILES.getlist('images'):
                ReviewImage.objects.create(review=new_review, image=img)
            
            return redirect('detail', book_id=book.id)
    
    context = {
        'book': book,
        'reviews': reviews,
        'related_books': related_books,
        'form': review_form,
    }
    return render(request, 'shop/book_detail.html', context)

def author_detail(request, author_id):
    author = get_object_or_404(Authors, id=author_id)
    books = Book.objects.filter(authors=author)
    
    context = {
        'author': author,
        'books': books,
    }
    return render(request, 'shop/author_detail.html', context)


def category_books(request, genre_id):
    genre = get_object_or_404(Genres, id=genre_id)
    books_list = Book.objects.filter(genres=genre)
    
    paginator = Paginator(books_list, 8)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    context = {
        'genre': genre,
        'books': books,
    }
    return render(request, 'shop/category_books.html', context)

def language_books(request, language_id):
    language = get_object_or_404(Languages, id=language_id)
    books_list = Book.objects.filter(languages=language)
    
    paginator = Paginator(books_list, 8)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    context = {
        'language': language,
        'books': books,
    }
    return render(request, 'shop/language_books.html', context)


def registration(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('homepage')
    else:
        form = CustomUserCreationForm()
        
        
    return render(request, 'users/registration.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            error_message = 'Invalid username or password.'
            return render(request, 'users/login.html', {'error_message': error_message})
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('homepage')

def profile(request):
    reviews = Review.objects.filter(user=request.user)
    if not request.user.is_authenticated:
        return redirect('login')
    
    
    context = {
        'user': request.user,
        'reviews': reviews,
    }
    return render(request, 'users/profile.html', context)

def update_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'users/update_profile.html', context)


def _get_cart(session):
    """Return cart dict from session. Structure: {book_id: quantity} """
    return session.get('cart', {})


def _save_cart(session, cart):
    session['cart'] = cart
    session.modified = True


def add_to_cart(request, book_id):
    # Only support POST
    if request.method != 'POST':
        return redirect('detail', book_id=book_id)

    cart = _get_cart(request.session)
    qty = int(request.POST.get('quantity', 1))
    # ensure qty >=1
    if qty < 1:
        qty = 1

    book = get_object_or_404(Book, id=book_id)
    cart[str(book_id)] = cart.get(str(book_id), 0) + qty
    _save_cart(request.session, cart)

    # If request is AJAX, return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'cart_count': sum(cart.values())})

    return redirect('cart')


def cart_view(request):
    cart = _get_cart(request.session)
    items = []
    total = 0
    book_ids = [int(k) for k in cart.keys()]
    books = Book.objects.filter(id__in=book_ids)
    books_map = {b.id: b for b in books}
    for k, v in cart.items():
        bid = int(k)
        book = books_map.get(bid)
        if not book:
            continue
        quantity = int(v)
        subtotal = (book.price or 0) * quantity
        total += subtotal
        items.append({'book': book, 'quantity': quantity, 'subtotal': subtotal})

    context = {'items': items, 'total': total}
    return render(request, 'shop/cart.html', context)


def update_cart(request):
    # expects POST with pairs book_id -> quantity
    if request.method != 'POST':
        return redirect('cart')

    cart = _get_cart(request.session)
    changed = False
    for key, val in request.POST.items():
        if not key.startswith('qty_'):
            continue
        try:
            book_id = key.split('_', 1)[1]
            qty = int(val)
        except Exception:
            continue
        if qty <= 0:
            if book_id in cart:
                del cart[book_id]
                changed = True
        else:
            cart[book_id] = qty
            changed = True

    if changed:
        _save_cart(request.session, cart)

    return redirect('cart')


def remove_from_cart(request, book_id):
    cart = _get_cart(request.session)
    book_id = str(book_id)
    if book_id in cart:
        del cart[book_id]
        _save_cart(request.session, cart)
    return redirect('cart')


def saved_books(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        if book in request.user.saved_books.all():
            request.user.saved_books.remove(book)
        else:
            request.user.saved_books.add(book)
        return redirect('saved_books')
    
    books = request.user.saved_books.all()
    
    context = {
        'books': books,
    }
    return render(request, 'shop/saved_books.html', context)

def cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        if book in request.user.cart_books.all():
            request.user.cart_books.remove(book)
        else:
            request.user.cart_books.add(book)
        return redirect('cart')
    
    books = request.user.cart_books.all()
    
    context = {
        'books': books,
    }
    return render(request, 'shop/cart.html', context)