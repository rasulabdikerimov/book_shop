from django.urls import path
from . import views
urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('search/', views.search_results, name='search_results'),
    path('popular-books/', views.popular_books, name='popular_books'),
    path('book/<int:book_id>/', views.book_detail, name='detail'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('genre/<int:genre_id>/', views.category_books, name='category_books'),
    path('language/<int:language_id>/', views.language_books, name='language_books'),
    path('register/', views.registration, name='registration'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.update_profile, name='update_profile'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('saved-books/', views.saved_books, name='saved_books'),
    path('cart/', views.cart, name='cart'),
    ]