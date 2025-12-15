from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from shop.models import Book, Order, CustomUser, Review, Delivery, Payment, Genres, Languages, Countries, Authors
from .forms import AdminBookForm, AdminReviewForm, AdminUserForm, AdminGenreForm, AdminAuthorForm
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import AdminSendNotificationForm
from django.contrib import messages
from shop.models import Notification, NotificationRecipient


def _staff_required(view_func):
	def _wrapped(request, *args, **kwargs):
		if not request.user.is_authenticated:
			return redirect('login')
		if not request.user.is_staff:
			return redirect('homepage')
		return view_func(request, *args, **kwargs)
	return _wrapped
@_staff_required
def dashboard(request):
	books_count = Book.objects.count()
	users_count = CustomUser.objects.count()
	orders_count = Order.objects.count()
	reviews_count = Review.objects.count()
	latest_books = Book.objects.order_by('-id')[:5]

	context = {
		'books_count': books_count,
		'users_count': users_count,
		'orders_count': orders_count,
		'reviews_count': reviews_count,
		'latest_books': latest_books,
	}
	return render(request, 'adminpanel/dashboard.html', context)
@_staff_required
def users_list(request):
	users = CustomUser.objects.all().order_by('-id')
	return render(request, 'adminpanel/users.html', {'users': users})


@_staff_required
def books_list(request):
	from django.core.paginator import Paginator

	books_all = Book.objects.all().order_by('-id')
	paginator = Paginator(books_all, 20)
	page_number = request.GET.get('page')
	books = paginator.get_page(page_number)

	context = {
		'books': books,
		'total_books': books_all.count(),
	}
	return render(request, 'adminpanel/books.html', context)


@_staff_required
def orders_list(request):
	from django.core.paginator import Paginator
	from django.db.models import Q, Sum

	
	orders_qs = Order.objects.select_related('user').prefetch_related('book', 'payment_set', 'delivery_set').order_by('-created_at')

	payment_status = (request.GET.get('payment_status') or '').strip()
	delivery_status = (request.GET.get('delivery_status') or '').strip()
	date_from = (request.GET.get('date_from') or '').strip()
	date_to = (request.GET.get('date_to') or '').strip()
	price_from = (request.GET.get('price_from') or '').strip()
	price_to = (request.GET.get('price_to') or '').strip()
	customer = (request.GET.get('customer') or '').strip()
	product = (request.GET.get('product') or '').strip()

	q = Q()

	if payment_status:
		q &= Q(payment__status=payment_status)

	if delivery_status:
		q &= Q(delivery__status=delivery_status)

	if date_from:
		q &= Q(created_at__gte=date_from)
	if date_to:
		q &= Q(created_at__lte=date_to)

	if price_from:
		try:
			q &= Q(total_price__gte=int(price_from))
		except ValueError:
			pass
	if price_to:
		try:
			q &= Q(total_price__lte=int(price_to))
		except ValueError:
			pass

	if customer:
		q &= (Q(user__email__icontains=customer) | Q(user__username__icontains=customer))

	if product:
		q &= Q(book__title__icontains=product)

	# Apply filters and ensure distinct results (joins can duplicate rows)
	if q:
		orders_all = orders_qs.filter(q).distinct()
	else:
		orders_all = orders_qs

	# Pagination
	paginator = Paginator(orders_all, 10)
	page_number = request.GET.get('page')
	orders = paginator.get_page(page_number)

	# Aggregates
	total_sales = orders_all.aggregate(total=Sum('total_price'))['total'] or 0
	total_count = orders_all.count()
	average_order = int(total_sales / total_count) if total_count > 0 else 0

	context = {
		'orders': orders,
		'total_sales': total_sales,
		'average_order': average_order,
		'total_orders': total_count,

		'payment_status': payment_status,
		'delivery_status': delivery_status,
		'date_from': date_from,
		'price_from': price_from,
		'price_to': price_to,
		'customer': customer,
		'product': product,
	}
	return render(request, 'adminpanel/orders.html', context)


@_staff_required
def reviews_list(request):
	reviews = Review.objects.select_related('user', 'book').order_by('-created_at')
	return render(request, 'adminpanel/reviews.html', {'reviews': reviews})


@_staff_required
def review_edit(request, review_id):
	review = get_object_or_404(Review, id=review_id)
	if request.method == 'POST':
		form = AdminReviewForm(request.POST, instance=review)
		if form.is_valid():
			form.save()
			return redirect('adminpanel:reviews')
	else:
		form = AdminReviewForm(instance=review)
	return render(request, 'adminpanel/book_form.html', {'form': form, 'title': 'Редактировать отзыв'})


@_staff_required
def user_edit(request, user_id):
	user = get_object_or_404(CustomUser, id=user_id)
	if request.method == 'POST':
		form = AdminUserForm(request.POST, request.FILES, instance=user)
		if form.is_valid():
			form.save()
			return redirect('adminpanel:users')
	else:
		form = AdminUserForm(instance=user)
	return render(request, 'adminpanel/book_form.html', {'form': form, 'title': 'Редактировать пользователя'})


@_staff_required
def book_create(request):
	if request.method == 'POST':
		form = AdminBookForm(request.POST, request.FILES)
		if form.is_valid():
			b = form.save()
			return redirect('adminpanel:books')
	else:
		form = AdminBookForm()
	return render(request, 'adminpanel/book_form.html', {'form': form, 'title': 'Создать книгу'})


@_staff_required
def book_edit(request, book_id):
	book = get_object_or_404(Book, id=book_id)
	if request.method == 'POST':
		form = AdminBookForm(request.POST, request.FILES, instance=book)
		if form.is_valid():
			form.save()
			return redirect('adminpanel:books')
	else:
		form = AdminBookForm(instance=book)
	return render(request, 'adminpanel/book_form.html', {'form': form, 'title': 'Редактировать книгу'})


@_staff_required
def book_delete(request, book_id):
	book = get_object_or_404(Book, id=book_id)
	if request.method == 'POST':
		book.delete()
		return redirect('adminpanel:books')
	return render(request, 'adminpanel/confirm_delete.html', {'obj': book, 'type':'book'})


@_staff_required
def review_delete(request, review_id):
	review = get_object_or_404(Review, id=review_id)
	if request.method == 'POST':
		review.delete()
		return redirect('adminpanel:reviews')
	return render(request, 'adminpanel/confirm_delete.html', {'obj': review, 'type':'review'})


@_staff_required
def user_toggle(request, user_id):
	u = get_object_or_404(CustomUser, id=user_id)
	u.is_active = not u.is_active
	u.save()
	return redirect('adminpanel:users')


@_staff_required
def order_detail(request, order_id):

	order = get_object_or_404(Order, id=order_id)
	books = order.book.all()
	payment = order.payment_set.first()
	delivery = order.delivery_set.first()
	
	context = {
		'order': order,
		'books': books,
		'payment': payment,
		'delivery': delivery,
	}
	return render(request, 'adminpanel/order_detail.html', context)


@_staff_required
def order_update_status(request, order_id):

	order = get_object_or_404(Order, id=order_id)
	payment = order.payment_set.first()
	delivery = order.delivery_set.first()
	
	if request.method == 'POST':
		new_status = request.POST.get('status')
		if new_status and payment:
	
			if new_status == 'Завершен':
				payment.mark_as_completed()
			else:
				payment.status = new_status
				payment.save()
		return redirect('adminpanel:order_detail', order_id=order.id)
	
	context = {
		'order': order,
		'payment': payment,
		'delivery': delivery,
		'statuses': ['В ожидании', 'Завершен', 'Отменен'],
	}
	return render(request, 'adminpanel/order_update_status.html', context)


@_staff_required
def send_message(request):
	# Allows admin to send a notification to multiple users (originates from carts view)
	if request.method == 'POST':
		form = AdminSendNotificationForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			message_text = form.cleaned_data['message']
			users = form.cleaned_data['users']

			notif = Notification.objects.create(sender=request.user, title=title, message=message_text)
			recipients = [NotificationRecipient(notification=notif, user=u) for u in users]
			NotificationRecipient.objects.bulk_create(recipients)
			messages.success(request, f'Отправлено {len(recipients)} сообщений.')
			return redirect('adminpanel:carts')
	else:
		initial_users = request.GET.getlist('users')
		form = AdminSendNotificationForm(initial={'users': initial_users})

	return render(request, 'adminpanel/send_message.html', {'form': form})


@_staff_required
def delivery_create(request, order_id):

	order = get_object_or_404(Order, id=order_id)
	
	if request.method == 'POST':
		delivery_address = request.POST.get('delivery_address', order.user.address).strip()
		delivery_date = request.POST.get('delivery_date', '').strip()
		
		delivery = Delivery.objects.create(
			order=order,
			delivery_address=delivery_address,
			delivery_date=delivery_date,
			status='В ожидании'
		)
		return redirect('adminpanel:order_detail', order_id=order.id)
	
	context = {
		'order': order,
	}
	return render(request, 'adminpanel/delivery_form.html', context)


@_staff_required
def delivery_update_status(request, delivery_id):
	
	delivery = get_object_or_404(Delivery, id=delivery_id)
	
	if request.method == 'POST':
		new_status = request.POST.get('status')
		if new_status:
		
			if new_status == 'Завершена':
				delivery.mark_as_delivered()
			else:
				delivery.status = new_status
				delivery.save()
		return redirect('adminpanel:order_detail', order_id=delivery.order.id)
	
	context = {
		'delivery': delivery,
		'statuses': ['В ожидании', 'В пути', 'Завершена', 'Отменена'],
	}
	return render(request, 'adminpanel/delivery_update_status.html', context)


@_staff_required
def deliveries_list(request):
	
	from django.core.paginator import Paginator
	
	deliveries_all = Delivery.objects.select_related('order', 'employee').order_by('-created_at')
	paginator = Paginator(deliveries_all, 15)
	page_number = request.GET.get('page')
	deliveries = paginator.get_page(page_number)
	
	context = {
		'deliveries': deliveries,
		'total_deliveries': deliveries_all.count(),
	}
	return render(request, 'adminpanel/deliveries.html', context)


@_staff_required
def genres_list(request):

	from django.core.paginator import Paginator
	
	genres_all = Genres.objects.all().order_by('genre')
	paginator = Paginator(genres_all, 20)
	page_number = request.GET.get('page')
	genres = paginator.get_page(page_number)
	
	context = {
		'genres': genres,
		'total_genres': genres_all.count(),
	}
	return render(request, 'adminpanel/genres.html', context)


@_staff_required
def languages_list(request):

	from django.core.paginator import Paginator
	
	languages_all = Languages.objects.all().order_by('language')
	paginator = Paginator(languages_all, 20)
	page_number = request.GET.get('page')
	languages = paginator.get_page(page_number)
	
	context = {
		'languages': languages,
		'total_languages': languages_all.count(),
	}
	return render(request, 'adminpanel/languages.html', context)


@_staff_required
def countries_list(request):
	
	from django.core.paginator import Paginator
	
	countries_all = Countries.objects.all().order_by('country')
	paginator = Paginator(countries_all, 20)
	page_number = request.GET.get('page')
	countries = paginator.get_page(page_number)
	
	context = {
		'countries': countries,
		'total_countries': countries_all.count(),
	}
	return render(request, 'adminpanel/countries.html', context)


@_staff_required
def authors_list(request):

	from django.core.paginator import Paginator
	
	authors_all = Authors.objects.all().order_by('full_name')
	paginator = Paginator(authors_all, 15)
	page_number = request.GET.get('page')
	authors = paginator.get_page(page_number)
	
	context = {
		'authors': authors,
		'total_authors': authors_all.count(),
	}
	return render(request, 'adminpanel/authors.html', context)


@_staff_required
def carts_list(request):
	from django.core.paginator import Paginator
	
	CartModel = __import__('shop.models', fromlist=['Cart']).Cart
	carts_all = CartModel.objects.select_related('user').prefetch_related('book').order_by('-id')

	
	from django.contrib.sessions.models import Session
	from django.contrib.auth import get_user_model
	User = get_user_model()
	session_carts = []
	for sess in Session.objects.all():
		try:
			data = sess.get_decoded()
		except Exception:
			continue
		cart = data.get('cart')
		if not cart:
			continue
		
		user = None
		uid = data.get('_auth_user_id')
		if uid:
			try:
				user = User.objects.filter(pk=uid).first()
			except Exception:
				user = None

	
		book_ids = [int(k) for k in cart.keys() if k.isdigit()]
		books = []
		books_with_counts = []
		if book_ids:
			BookModel = __import__('shop.models', fromlist=['Book']).Book
			books = list(BookModel.objects.filter(id__in=book_ids))
		
			for bid in book_ids:
				try:
					b = next(x for x in books if x.id == bid)
				except StopIteration:
					continue
				qty = int(cart.get(str(bid), 0))
				books_with_counts.append({'book': b, 'qty': qty})

		session_carts.append({
			'session_key': sess.session_key,
			'user': user,
			'books_with_counts': books_with_counts,
			'total_items': sum(x['qty'] for x in books_with_counts) if books_with_counts else 0,
		})

	paginator = Paginator(carts_all, 20)
	page_number = request.GET.get('page')
	carts = paginator.get_page(page_number)


	try:
		UserCartItem = __import__('shop.models', fromlist=['UserCartItem']).UserCartItem
		user_carts_qs = UserCartItem.objects.select_related('book', 'user').order_by('user__id')
		user_carts = {}
		for item in user_carts_qs:
			uid = item.user.id
			if uid not in user_carts:
				user_carts[uid] = {'user': item.user, 'books_with_counts': [], 'total_items': 0}
			user_carts[uid]['books_with_counts'].append({'book': item.book, 'qty': item.quantity})
			user_carts[uid]['total_items'] += item.quantity
		# convert to list
		user_carts = list(user_carts.values())
	except Exception:
		user_carts = []

	context = {
		'carts': carts,
		'total_carts': carts_all.count(),
		'session_carts': session_carts,
		'user_carts': user_carts,
	}
	return render(request, 'adminpanel/carts.html', context)


@_staff_required
def product_views(request):
	from django.shortcuts import redirect

	if request.method == 'POST':
		book_id = request.POST.get('book_id')
		action = request.POST.get('action')
		next_url = request.POST.get('next') or None
		if book_id and action == 'increment':
			try:
				b = Book.objects.get(id=int(book_id))
				b.view_count = (b.view_count or 0) + 1
				b.save()
			except Book.DoesNotExist:
				pass
		if next_url:
			return redirect(next_url)
		return redirect('adminpanel:product_views')

	book_id = request.GET.get('book_id')
	if book_id:
		try:
			books = Book.objects.filter(id=int(book_id))
		except ValueError:
			books = Book.objects.none()
	else:
		books = Book.objects.all().order_by('-view_count', '-id')

	return render(request, 'adminpanel/product_views.html', {'books': books})


@_staff_required
def genre_create(request):
	from .forms import AdminGenreForm
	
	if request.method == 'POST':
		form = AdminGenreForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('adminpanel:genres_list')
	else:
		form = AdminGenreForm()
	
	context = {
		'form': form,
		'title': 'Добавить новый жанр',
		'button_text': 'Добавить жанр',
	}
	return render(request, 'adminpanel/model_form.html', context)


@_staff_required
def genre_edit(request, genre_id):
	from .forms import AdminGenreForm
	
	genre = get_object_or_404(Genres, id=genre_id)
	
	if request.method == 'POST':
		form = AdminGenreForm(request.POST, instance=genre)
		if form.is_valid():
			form.save()
			return redirect('adminpanel:genres_list')
	else:
		form = AdminGenreForm(instance=genre)
	
	context = {
		'form': form,
		'title': f'Редактировать жанр: {genre.genre}',
		'button_text': 'Сохранить изменения',
	}
	return render(request, 'adminpanel/model_form.html', context)


@_staff_required
def genre_delete(request, genre_id):
	genre = get_object_or_404(Genres, id=genre_id)
	
	if request.method == 'POST':
		genre.delete()
		return redirect('adminpanel:genres_list')
	
	context = {
		'object': genre,
		'object_name': genre.genre,
		'model_name': 'жанр',
		'cancel_url': 'adminpanel:genres_list',
	}
	return render(request, 'adminpanel/confirm_delete.html', context)


@_staff_required
def author_create(request):
	
	from .forms import AdminAuthorForm
	
	if request.method == 'POST':
		form = AdminAuthorForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('adminpanel:authors_list')
	else:
		form = AdminAuthorForm()
	
	context = {
		'form': form,
		'title': 'Добавить нового автора',
		'button_text': 'Добавить автора',
	}
	return render(request, 'adminpanel/model_form.html', context)


@_staff_required
def author_edit(request, author_id):
	
	from .forms import AdminAuthorForm
	
	author = get_object_or_404(Authors, id=author_id)
	
	if request.method == 'POST':
		form = AdminAuthorForm(request.POST, request.FILES, instance=author)
		if form.is_valid():
			form.save()
			return redirect('adminpanel:authors_list')
	else:
		form = AdminAuthorForm(instance=author)
	
	context = {
		'form': form,
		'title': f'Редактировать автора: {author.full_name}',
		'button_text': 'Сохранить изменения',
	}
	return render(request, 'adminpanel/model_form.html', context)


@_staff_required
def author_delete(request, author_id):
	
	author = get_object_or_404(Authors, id=author_id)
	
	if request.method == 'POST':
		author.delete()
		return redirect('adminpanel:authors_list')
	
	context = {
		'object': author,
		'object_name': author.full_name,
		'model_name': 'автора',
		'cancel_url': 'adminpanel:authors_list',
	}
	return render(request, 'adminpanel/confirm_delete.html', context)


@_staff_required
def analytics(request):

	from datetime import datetime, timedelta
	from django.db.models import Count, Sum, Q
	from django.utils import timezone
	import json
	

	period = request.GET.get('period', 'month')
	# sort can be 'sales' or 'views'
	sort = request.GET.get('sort', 'sales')
	

	now = timezone.now()
	if period == 'year':
		start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
		period_name = f"{now.year} год"
	else: 
		start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		period_name = f"{now.strftime('%B %Y')}"
	
	
	# Build top_books according to chosen sort
	if sort == 'views':
		# Order by global view_count but still annotate sales_count for display
		top_books = Book.objects.annotate(sales_count=Count('order')).order_by('-view_count')[:10]
		books_labels = [b.title[:20] for b in top_books]
		books_data = [b.view_count or 0 for b in top_books]
		books_metric_label = 'Просмотры'
	else:
		# Default: top by sales in the selected period
		top_books = Book.objects.filter(
			order__created_at__gte=start_date
		).annotate(
			sales_count=Count('order')
		).order_by('-sales_count')[:10]
		books_labels = [b.title[:20] for b in top_books]
		books_data = [b.sales_count for b in top_books]
		books_metric_label = 'Продаж'

	if period == 'year':
	
		orders_by_month = []
		revenue_by_month = []
		for month in range(1, 13):
			month_start = now.replace(month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
			if month == 12:
				month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
			else:
				month_end = month_start.replace(month=month + 1, day=1)
			
			revenue = Order.objects.filter(
				created_at__gte=month_start,
				created_at__lt=month_end,
				cancel_status='Активен'
			).aggregate(total=Sum('total_price'))['total'] or 0
			revenue_by_month.append(revenue)
			orders_by_month.append(f"Мес {month}")
	else:
	
		orders_by_month = []
		revenue_by_month = []
		days_in_month = (start_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
		for day in range(1, days_in_month.day + 1):
			day_start = start_date.replace(day=day, hour=0, minute=0, second=0, microsecond=0)
			day_end = day_start + timedelta(days=1)
			
			revenue = Order.objects.filter(
				created_at__gte=day_start,
				created_at__lt=day_end,
				cancel_status='Активен'
			).aggregate(total=Sum('total_price'))['total'] or 0
			revenue_by_month.append(revenue)
			orders_by_month.append(f"День {day}")
	

	top_customers = CustomUser.objects.filter(
		order__created_at__gte=start_date
	).annotate(
		orders_count=Count('order'),
		total_spent=Sum('order__total_price')
	).order_by('-total_spent')[:10]
	
	customers_labels = [u.username[:15] for u in top_customers]
	customers_data = [u.total_spent or 0 for u in top_customers]
	

	reviews_by_rating = Review.objects.filter(
		created_at__gte=start_date
	).values('stars').annotate(count=Count('id')).order_by('stars')
	
	ratings_labels = [f"{r['stars']}★" for r in reviews_by_rating]
	ratings_data = [r['count'] for r in reviews_by_rating]

	if not ratings_labels:
		ratings_labels = ["1★", "2★", "3★", "4★", "5★"]
		ratings_data = [0, 0, 0, 0, 0]
	
	payment_statuses = Order.objects.filter(
		created_at__gte=start_date
	).values('payment__status').annotate(count=Count('id')).order_by('payment__status')
	
	status_labels = [s['payment__status'] or 'Не указан' for s in payment_statuses]
	status_data = [s['count'] for s in payment_statuses]

	genres_stats = Book.objects.filter(
		order__created_at__gte=start_date
	).values('genres__genre').annotate(count=Count('order')).order_by('-count')[:8]
	
	genres_labels = [g['genres__genre'] for g in genres_stats]
	genres_data = [g['count'] for g in genres_stats]
	
	context = {
		'period': period,
		'period_name': period_name,
		'books_labels': json.dumps(books_labels),
		'books_data': json.dumps(books_data),
		'books_metric_label': books_metric_label,
		'sort': sort,
		'orders_labels': json.dumps(orders_by_month),
		'revenue_data': json.dumps(revenue_by_month),
		'customers_labels': json.dumps(customers_labels),
		'customers_data': json.dumps(customers_data),
		'ratings_labels': json.dumps(ratings_labels),
		'ratings_data': json.dumps(ratings_data),
		'status_labels': json.dumps(status_labels),
		'status_data': json.dumps(status_data),
		'genres_labels': json.dumps(genres_labels),
		'genres_data': json.dumps(genres_data),
		'top_customers': top_customers,
		'top_books': top_books,
	}
	return render(request, 'adminpanel/analytics.html', context)
