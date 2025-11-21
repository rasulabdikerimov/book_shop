
from email.mime import image
from pyexpat import model
from statistics import mode
from django.db import models
from django.contrib.auth.models import AbstractUser
import random
# Create your models here.

class CustomUser(AbstractUser):

    email = models.EmailField(unique=True,
                              verbose_name='Электронная почта:')
    phone_number = models.CharField(max_length=15,
                                    verbose_name='Номер телефона:')
    address = models.CharField(max_length=255,
                               verbose_name='Адрес доставки:')
    image = models.ImageField(upload_to='users/',
                              verbose_name='Фото пользователя:',
                              null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    

class Genres(models.Model):
    genre = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.genre
class Languages(models.Model):
    language = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.language
    
class Countries(models.Model):
    country = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.country
    

class Authors(models.Model):
    full_name = models.CharField(max_length=100,
                                 verbose_name='ФИО автора:')
    birth_date = models.CharField(max_length=100,
                                  verbose_name='Дата рождения автора:',help_text='Формат: ДД.ММ.ГГГГ')
    country = models.ForeignKey(Countries, on_delete=models.CASCADE,
                                verbose_name='Страна автора:')
    photo = models.ImageField(upload_to='authors/',
                              verbose_name='Фото автора:')
    biography = models.TextField(verbose_name='Биография автора:')
    review = models.ManyToManyField('Review', verbose_name='Отзывы об авторе:', blank=True)


    def __str__(self):
        return self.full_name
    
class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь:')
    book = models.ForeignKey('Book', on_delete=models.CASCADE, verbose_name='Книга:')
    stars = models.IntegerField(verbose_name='Рейтинг:')
    comment = models.TextField(verbose_name='Комментарий:')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания отзыва:')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления отзыва:')
    images = models.ManyToManyField('ReviewImage', verbose_name='Фото к отзыву:', blank=True)

    def __str__(self) -> str:
        return f'Review by {self.user.username} for {self.book.title}'


class ReviewImage(models.Model):
    image = models.ImageField(upload_to='reviews/', verbose_name='Фото к отзыву:')
    def __str__(self) -> str:
        return self.image.url


class Book(models.Model):
    title = models.CharField(max_length=100,
                             verbose_name='Названия книги:')
    description = models.TextField(verbose_name='Описания книги:')
    pub_date = models.CharField(verbose_name='Дата публикации:',max_length=4,help_text='Формат: ГГГГ')
    price = models.IntegerField(verbose_name='Цена книги:')
    photo = models.ImageField(upload_to='books/', verbose_name='Фото книги:')
    genres = models.ManyToManyField(Genres, verbose_name='Жанр книги:')
    languages = models.ManyToManyField(Languages, verbose_name='Язык книги:')
    authors = models.ManyToManyField(Authors, verbose_name='Автор книги:')


    def __str__(self) -> str:
        return self.title
    
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь:')
    book = models.ManyToManyField(Book, verbose_name='Книга:')
    quantity = models.IntegerField(verbose_name='Количество книг:')
    

    def __str__(self) -> str:
        return f'Cart of {self.user.username}'
    
class Order(models.Model):
    order_number = models.CharField(max_length=6, unique=True, 
                                    verbose_name='Номер заказа:')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь:')
    book = models.ManyToManyField(Book, verbose_name='Книга:')
    total_price = models.IntegerField(verbose_name='Общая цена заказа:')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата создания заказа:')
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата обновления заказа:')

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Order #{self.order_number} - {self.user.username}'
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              verbose_name='Заказ:')
    payment_method = models.CharField(max_length=100,
                                      verbose_name='Способ оплаты:')
    status = models.CharField(max_length=100,
                              verbose_name='Статус оплаты:',
                              default='В ожидании')
    
    payment_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name='Дата оплаты:')
    amount = models.IntegerField(verbose_name='Сумма оплаты:')

    def __str__(self) -> str:
        return f'Payment for Order #{self.order.order_number}'
    

class Delivery(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE,
                                 verbose_name='Сотрудник доставки:')
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              verbose_name='Заказ:')
    delivery_address = models.CharField(max_length=255,
                                        verbose_name='Адрес доставки:')
    delivery_date = models.CharField(max_length=100,
                                     verbose_name='Дата доставки:')
    status = models.CharField(max_length=100,
                              verbose_name='Статус доставки:',
                              default='В ожидании')

    def __str__(self) -> str:
        return f'Delivery for Order #{self.order.order_number}'
    

class Employee(models.Model):
    full_name = models.CharField(max_length=100,
                                 verbose_name='ФИО сотрудника:')
    position = models.CharField(max_length=100,
                                verbose_name='Должность сотрудника:')
    hire_date = models.CharField(max_length=100,
                                 verbose_name='Дата найма сотрудника:')
    photo = models.ImageField(upload_to='employees/',
                              verbose_name='Фото сотрудника:')
    review = models.ManyToManyField(Review, verbose_name='Отзывы о сотруднике:', blank=True)

    def __str__(self) -> str:
        return self.full_name