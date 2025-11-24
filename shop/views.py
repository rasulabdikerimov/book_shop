
from django.shortcuts import render,get_object_or_404
from .models import Book, Genres, Authors, Languages, Countries, Review, ReviewImage, CustomUser
# Create your views here.
from django.db.models import Q
def homepage(request):
    books = Book.objects.all()[:4]
    genres = Genres.objects.all()[:6]
    authors = Authors.objects.all()[:6]
    context = {
        'books': books,
        'genres': genres,
        'authors': authors,
    }
    return render(request, 'shop/homepage.html', context)

def popular_books(request):
    books = Book.objects.all()[:20]
    context = {
        'books': books,
    }
    return render(request, 'shop/popular_books.html', context)


def search_results(request):
    query = request.GET.get('q', '')

    print(query)
    books = Book.objects.filter(
        Q(title__icontains=query)|
        Q(authors__full_name__icontains=query)
        ).distinct()
    context = {
        'books': books,
        'query': query,
    }
    return render(request, 'shop/search_results.html', context)
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