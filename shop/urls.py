from django.urls import path
from . import views
urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('search/', views.search_results, name='search_results'),
    path('popular-books/', views.popular_books, name='popular_books'),
    path('book/<int:book_id>/', views.book_detail, name='detail'),
    ]