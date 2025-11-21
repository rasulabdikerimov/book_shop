
from django.shortcuts import render,get_object_or_404
from .models import Book, Genres, Authors, Languages, Countries, Review, ReviewImage, CustomUser
# Create your views here.

def homepage(request):
    books = Book.objects.all()
    genres = Genres.objects.all()
    authors = Authors.objects.all()
    languages = Languages.objects.all()
    countries = Countries.objects.all()
    reviews = Review.objects.all()
    review_images = ReviewImage.objects.all()
    users = CustomUser.objects.all()
    context = {
        'books': books,
        'genres': genres,
        'authors': authors,
    }
    return render(request, 'shop/homepage.html', context)

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    author = get_object_or_404(Authors, id=book_id)
    context = {
        'book': book,
        'author': author,
    }
    return render(request, 'shop/book_detail.html', context)
    