from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('books/', views.books_list, name='books'),
    path('books/add/', views.book_create, name='book_create'),
    path('books/<int:book_id>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:book_id>/delete/', views.book_delete, name='book_delete'),
    path('users/', views.users_list, name='users'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/toggle/', views.user_toggle, name='user_toggle'),
    path('orders/', views.orders_list, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.order_update_status, name='order_update_status'),
    path('reviews/', views.reviews_list, name='reviews'),
    path('reviews/<int:review_id>/edit/', views.review_edit, name='review_edit'),
    path('reviews/<int:review_id>/delete/', views.review_delete, name='review_delete'),
]
