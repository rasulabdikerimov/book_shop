from django.contrib import admin
from .models import CustomUser, Genres, Languages, Countries, Authors, Review, ReviewImage, Book
from django.contrib import admin
from .models import (CustomUser, Genres, Languages, Countries, Authors, 
                     Review, ReviewImage, Book, Cart, Order, Payment, Delivery, Employee)

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Genres)
admin.site.register(Languages)
admin.site.register(Countries)
admin.site.register(Authors)
admin.site.register(Review)
admin.site.register(ReviewImage)
admin.site.register(Book)
admin.site.register(Cart)
from .models import UserCartItem
admin.site.register(UserCartItem)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Delivery)
admin.site.register(Employee)
from .models import Notification, NotificationRecipient

admin.site.register(Notification)
admin.site.register(NotificationRecipient)

