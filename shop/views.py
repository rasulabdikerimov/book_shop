
from django.shortcuts import render,get_object_or_404
from .models import Book, Genres, Authors, Languages, Countries, Review, ReviewImage, CustomUser
# Create your views here.

def homepage(request):
    books = Book.objects.all()
    genres = Genres.objects.all()
    authors = Authors.objects.all()
    context = {
        'books': books,
        'genres': genres,
        'authors': authors,
    }
    return render(request, 'shop/homepage.html', context)

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = Review.objects.filter(book=book).select_related('user')
    related_books = Book.objects.filter(genres__in=book.genres.all()).exclude(id=book_id).distinct()[:4]
    
    context = {
        'book': book,
        'reviews': reviews,
        'related_books': related_books,
    }
    return render(request, 'shop/book_detail.html', context)