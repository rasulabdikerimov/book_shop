from django.contrib import admin
from .models import CustomUser, Genres, Languages, Countries, Authors, Review, ReviewImage, Book
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Genres)
admin.site.register(Languages)
admin.site.register(Countries)
admin.site.register(Authors)
admin.site.register(Review)
admin.site.register(ReviewImage)
admin.site.register(Book)