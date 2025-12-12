
from django.shortcuts import redirect, render,get_object_or_404
from .models import Book, Genres, Authors, Languages, Countries, Review, ReviewImage, CustomUser, Order, Payment
# Create your views here.
from django.db.models import Q, F
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, ReviewForm,CustomUserChangeForm
from django.contrib.auth import login,authenticate,logout
from django.http import JsonResponse
def homepage(request):
    books = Book.objects.filter(stock__gt=0)[:4]
    genres = Genres.objects.all()[:6]
    authors = Authors.objects.all()[:6]
    context = {
        'books': books,
        'genres': genres,
        'authors': authors,
    }
    return render(request, 'shop/homepage.html', context)

def popular_books(request):
    books_list = Book.objects.filter(stock__gt=0)
    paginator = Paginator(books_list, 8)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    context = {
        'books': books,
    }
    return render(request, 'shop/popular_books.html', context)


def search_results(request):
    from urllib.parse import urlencode
    

    q = request.GET.get('q', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    year_from = request.GET.get('year_from', '').strip()
    year_to = request.GET.get('year_to', '').strip()
    author_slug = request.GET.get('author', '').strip()
    genre_slug = request.GET.get('genre', '').strip()
    language_slug = request.GET.get('language', '').strip()

    books_qs = Book.objects.filter(stock__gt=0)
    
   
    if q:
        books_qs = books_qs.filter(
            Q(title__icontains=q) |
            Q(authors__full_name__icontains=q)
        )
    
 
    if min_price:
        try:
            books_qs = books_qs.filter(price__gte=int(min_price))
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            books_qs = books_qs.filter(price__lte=int(max_price))
        except (ValueError, TypeError):
            pass
    

    if year_from:
        books_qs = books_qs.filter(pub_date__gte=year_from)
    
    if year_to:
        books_qs = books_qs.filter(pub_date__lte=year_to)
    
 
    if author_slug:
        books_qs = books_qs.filter(authors__slug=author_slug)
    
    if genre_slug:
        books_qs = books_qs.filter(genres__slug=genre_slug)
    
    if language_slug:
        books_qs = books_qs.filter(languages__slug=language_slug)


    books_qs = books_qs.distinct()


    paginator = Paginator(books_qs, 8)
    page_number = request.GET.get('page', 1)
    books = paginator.get_page(page_number)

    authors = Authors.objects.all()
    genres = Genres.objects.all()
    languages = Languages.objects.all()

    query_params = {}
    if q:
        query_params['q'] = q
    if min_price:
        query_params['min_price'] = min_price
    if max_price:
        query_params['max_price'] = max_price
    if year_from:
        query_params['year_from'] = year_from
    if year_to:
        query_params['year_to'] = year_to
    if author_slug:
        query_params['author'] = author_slug
    if genre_slug:
        query_params['genre'] = genre_slug
    if language_slug:
        query_params['language'] = language_slug
    
    base_query = urlencode(query_params) if query_params else ''
    context = {
        'books': books,
        'query': q,
        'min_price': min_price,
        'max_price': max_price,
        'year_from': year_from,
        'year_to': year_to,
        'selected_author': author_slug,
        'selected_genre': genre_slug,
        'selected_language': language_slug,
        'authors': authors,
        'genres': genres,
        'languages': languages,
        'base_query': base_query,
    }
    
    show_advanced = bool(request.GET.get('show_advanced'))
    context['show_advanced'] = show_advanced
    return render(request, 'shop/search_results.html', context)
def book_detail(request, book_slug):
    book = get_object_or_404(Book, slug=book_slug)
    # Increment view count atomically on GET
    if request.method == 'GET':
        try:
            Book.objects.filter(pk=book.pk).update(view_count=F('view_count') + 1)
            # refresh the instance so template shows updated count
            book.refresh_from_db(fields=['view_count'])
        except Exception:
            # avoid breaking page if update fails
            pass
    reviews = Review.objects.filter(book=book).select_related('user')
    related_books = Book.objects.filter(genres__in=book.genres.all()).exclude(id=book.id).distinct()[:4]

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
            
         
            for img in request.FILES.getlist('images'):
                ReviewImage.objects.create(review=new_review, image=img)
            
            return redirect('detail', book_slug=book.slug)
    
    context = {
        'book': book,
        'reviews': reviews,
        'related_books': related_books,
        'form': review_form,
    }
    return render(request, 'shop/book_detail.html', context)

def author_detail(request, author_slug):
    author = get_object_or_404(Authors, slug=author_slug)
    books = Book.objects.filter(authors=author, stock__gt=0)
  
    author_reviews = author.review.all()
   
    author_orders = Order.objects.filter(book__authors=author).distinct().order_by('-created_at')[:10]
    
    context = {
        'author': author,
        'books': books,
        'author_reviews': author_reviews,
        'author_orders': author_orders,
    }
    return render(request, 'shop/author_detail.html', context)


def category_books(request, genre_slug):
    genre = get_object_or_404(Genres, slug=genre_slug)
    books_list = Book.objects.filter(genres=genre, stock__gt=0)
    
    paginator = Paginator(books_list, 8)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    context = {
        'genre': genre,
        'books': books,
    }
    return render(request, 'shop/category_books.html', context)

def language_books(request, language_slug):
    language = get_object_or_404(Languages, slug=language_slug)
    books_list = Book.objects.filter(languages=language, stock__gt=0)
    
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
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {
        'user': request.user,
        'reviews': reviews,
        'orders': orders,
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
   
    return session.get('cart', {})


def _save_cart(session, cart):
    session['cart'] = cart
    session.modified = True


def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method != 'POST':
        return redirect('detail', book_slug=book.slug)

    cart = _get_cart(request.session)
    qty = int(request.POST.get('quantity', 1))
 
    if qty < 1:
        qty = 1

    cart[str(book_id)] = cart.get(str(book_id), 0) + qty
    _save_cart(request.session, cart)

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


def checkout(request):
   
    if not request.user.is_authenticated:
        return redirect('login')
    
    cart = _get_cart(request.session)
    if not cart:
        return redirect('cart')
    
    if request.method == 'POST':
    
        delivery_address = request.POST.get('delivery_address', request.user.address).strip()
        payment_method = request.POST.get('payment_method', 'card').strip()
     
        book_ids = [int(k) for k in cart.keys()]
        books = Book.objects.filter(id__in=book_ids)
        
        if not books:
            return redirect('cart')
        
        # Вычисляем общую цену
        total_price = 0
        for book in books:
            qty = int(cart.get(str(book.id), 0))
            total_price += (book.price or 0) * qty
        
        # Создаём заказ
        order = Order.objects.create(
            user=request.user,
            total_price=total_price
        )
        # Добавляем книги в заказ (товар будет вычтен только после оплаты и доставки)
        for book in books:
            qty = int(cart.get(str(book.id), 0))
            order.book.add(book)
        
        # Создаём запись платежа
        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            status='В ожидании',
            amount=total_price
        )
        
        # Очищаем корзину
        _save_cart(request.session, {})
        
        return redirect('order_confirmation', order_id=order.id)
    
    # GET: показываем форму оформления
    book_ids = [int(k) for k in cart.keys()]
    books = Book.objects.filter(id__in=book_ids)
    
    total_price = 0
    items = []
    for book in books:
        qty = int(cart.get(str(book.id), 0))
        subtotal = (book.price or 0) * qty
        total_price += subtotal
        items.append({'book': book, 'quantity': qty, 'subtotal': subtotal})
    
    context = {
        'items': items,
        'total_price': total_price,
        'user': request.user,
    }
    return render(request, 'shop/checkout.html', context)


def order_confirmation(request, order_id):
   
    order = get_object_or_404(Order, id=order_id, user=request.user)
    books = order.book.all()
    payment = order.payment_set.first()
    
    context = {
        'order': order,
        'books': books,
        'payment': payment,
    }
    return render(request, 'shop/order_confirmation.html', context)


def cancel_order(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.can_be_cancelled():
        return render(request, 'shop/order_confirmation.html', {
            'order': order,
            'books': order.book.all(),
            'payment': order.payment_set.first(),
            'error': 'Отмена невозможна: для заказа уже создана доставка.'
        })
    
    if request.method == 'POST':
        # Отмечаем заказ как отменен
        order.cancel_status = 'Отменен'
        order.save()
        
        # Отмечаем платеж как отменен
        payment = order.payment_set.first()
        if payment and payment.status == 'В ожидании':
            payment.status = 'Отменен'
            payment.save()
        
        return redirect('profile')
    
    context = {
        'order': order,
        'books': order.book.all(),
        'payment': order.payment_set.first(),
    }
    return render(request, 'shop/cancel_order_confirm.html', context)