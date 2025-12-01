from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from shop.models import Book, Order, CustomUser, Review
from .forms import AdminBookForm, AdminReviewForm, AdminUserForm
from django.urls import reverse
from django.views.decorators.http import require_POST


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
def books_list(request):
	books = Book.objects.all().order_by('-id')
	return render(request, 'adminpanel/books.html', {'books': books})


@_staff_required
def users_list(request):
	users = CustomUser.objects.all().order_by('-id')
	return render(request, 'adminpanel/users.html', {'users': users})


@_staff_required
def orders_list(request):
	orders = Order.objects.all().order_by('-created_at')
	return render(request, 'adminpanel/orders.html', {'orders': orders})


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
