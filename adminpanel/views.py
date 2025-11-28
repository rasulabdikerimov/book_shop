from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from shop.models import Book, Order, CustomUser, Review


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

	context = {
		'books_count': books_count,
		'users_count': users_count,
		'orders_count': orders_count,
		'reviews_count': reviews_count,
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
