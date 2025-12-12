from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
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
    path('orders/<int:order_id>/delivery/create/', views.delivery_create, name='delivery_create'),
    path('delivery/<int:delivery_id>/update-status/', views.delivery_update_status, name='delivery_update_status'),
    path('deliveries/', views.deliveries_list, name='deliveries'),
    path('genres/', views.genres_list, name='genres'),
    path('genres/add/', views.genre_create, name='genre_create'),
    path('genres/<int:genre_id>/edit/', views.genre_edit, name='genre_edit'),
    path('genres/<int:genre_id>/delete/', views.genre_delete, name='genre_delete'),
    path('languages/', views.languages_list, name='languages'),
    path('countries/', views.countries_list, name='countries'),
    path('authors/', views.authors_list, name='authors'),
    path('authors/add/', views.author_create, name='author_create'),
    path('authors/<int:author_id>/edit/', views.author_edit, name='author_edit'),
    path('authors/<int:author_id>/delete/', views.author_delete, name='author_delete'),
    path('reviews/', views.reviews_list, name='reviews'),
    path('reviews/<int:review_id>/edit/', views.review_edit, name='review_edit'),
    path('reviews/<int:review_id>/delete/', views.review_delete, name='review_delete'),
    path('carts/', views.carts_list, name='carts'),
    path('product-views/', views.product_views, name='product_views'),
]
