from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('books/', views.books_list, name='books'),
    path('users/', views.users_list, name='users'),
    path('orders/', views.orders_list, name='orders'),
    path('reviews/', views.reviews_list, name='reviews'),
]
