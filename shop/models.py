
from email.mime import image
from pyexpat import model
from statistics import mode
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.urls import reverse
import random
from django.conf import settings
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
    slug = models.SlugField(max_length=120, unique=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.genre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.genre)
            slug = base
            i = 1
            while Genres.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_books', kwargs={'genre_slug': self.slug})
class Languages(models.Model):
    language = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.language
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.language)
            slug = base
            i = 1
            while Languages.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('language_books', kwargs={'language_slug': self.slug})
    
class Countries(models.Model):
    country = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.country
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.country)
            slug = base
            i = 1
            while Countries.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)
    

class Authors(models.Model):
    full_name = models.CharField(max_length=100,
                                 verbose_name='ФИО автора:')
    slug = models.SlugField(max_length=140, unique=True, null=True, blank=True)
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
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.full_name)
            slug = base
            i = 1
            while Authors.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('author_detail', kwargs={'author_slug': self.slug})
    
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
    slug = models.SlugField(max_length=150, unique=True, null=True, blank=True)
    description = models.TextField(verbose_name='Описания книги:')
    pub_date = models.CharField(verbose_name='Дата публикации:',max_length=4,help_text='Формат: ГГГГ')
    price = models.IntegerField(verbose_name='Цена книги:')
    stock = models.IntegerField(verbose_name='Кол-во в наличии:', default=0, blank=True)
    photo = models.ImageField(upload_to='books/', verbose_name='Фото книги:')
    view_count = models.IntegerField(default=0, verbose_name='Количество просмотров:')
    genres = models.ManyToManyField(Genres, verbose_name='Жанр книги:')
    languages = models.ManyToManyField(Languages, verbose_name='Язык книги:')
    authors = models.ManyToManyField(Authors, verbose_name='Автор книги:')


    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            i = 1
            while Book.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detail', kwargs={'book_slug': self.slug})


class BookView(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Application logic will ensure uniqueness per (book, user) or (book, session_key)
        verbose_name = 'Book View'
        verbose_name_plural = 'Book Views'

    def __str__(self):
        if self.user:
            return f'View of {self.book.title} by {self.user}'
        return f'View of {self.book.title} by session {self.session_key}'


class UserCartItem(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='cart_items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.user.username} - {self.book.title} (x{self.quantity})'
    
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь:')
    book = models.ManyToManyField(Book, verbose_name='Книга:')
    quantity = models.IntegerField(verbose_name='Количество книг:')
    

    def __str__(self) -> str:
        return f'Cart of {self.user.username}'
    
class Order(models.Model):
    CANCEL_STATUS_CHOICES = [
        ('Активен', 'Активен'),
        ('Отменен', 'Отменен'),
    ]
    
    order_number = models.CharField(max_length=6, unique=True, 
                                    verbose_name='Номер заказа:')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             verbose_name='Пользователь:')
    book = models.ManyToManyField(Book, verbose_name='Книга:')
    total_price = models.IntegerField(verbose_name='Общая цена заказа:')
    stock_deducted = models.BooleanField(default=False, verbose_name='Товар вычтен:')
    cancel_status = models.CharField(max_length=20, 
                                     verbose_name='Статус отмены:',
                                     default='Активен',
                                     choices=CANCEL_STATUS_CHOICES)
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


class Notification(models.Model):
    sender = models.ForeignKey('CustomUser', null=True, blank=True, on_delete=models.SET_NULL,
                               related_name='sent_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification: {self.title}'


class NotificationRecipient(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('notification', 'user')

    def __str__(self):
        return f'NotificationRecipient: {self.user.username} - {self.notification.title}'
    
    def can_be_cancelled(self):
     
        delivery = self.delivery_set.first()
      
        return delivery is None
class Payment(models.Model):
    STATUS_CHOICES = [
        ('В ожидании', 'В ожидании'),
        ('Завершен', 'Завершен'),
        ('Отменен', 'Отменен'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              verbose_name='Заказ:')
    payment_method = models.CharField(max_length=100,
                                      verbose_name='Способ оплаты:')
    status = models.CharField(max_length=100,
                              verbose_name='Статус оплаты:',
                              default='В ожидании',
                              choices=STATUS_CHOICES)
    
    payment_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name='Дата оплаты:')
    amount = models.IntegerField(verbose_name='Сумма оплаты:')

    def __str__(self) -> str:
        return f'Payment for Order #{self.order.order_number}'
    
    def mark_as_completed(self):
        """Отметить платёж как завершённый и вычесть товар"""
        if self.status != 'Завершен':
            self.status = 'Завершен'
            self.save()
            # Вычитаем товар из наличия при завершении платежа только если ещё не вычли
            if not self.order.stock_deducted:
                for book in self.order.book.all():
                    qty = 1  # Можно модифицировать если добавить поле quantity в Order
                    book.stock -= qty
                    book.save()
                # Отмечаем что товар был вычтен
                self.order.stock_deducted = True
                self.order.save()
    

class Delivery(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.SET_NULL,
                                 verbose_name='Сотрудник доставки:', null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              verbose_name='Заказ:')
    delivery_address = models.CharField(max_length=255,
                                        verbose_name='Адрес доставки:')
    delivery_date = models.CharField(max_length=100,
                                     verbose_name='Дата доставки:', null=True, blank=True)
    status = models.CharField(max_length=100,
                              verbose_name='Статус доставки:',
                              default='В ожидании')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания:')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления:')

    def __str__(self) -> str:
        return f'Delivery for Order #{self.order.order_number}'
    
    def mark_as_delivered(self):
        """Отметить доставку как завершённую и вычесть товар из наличия"""
        if self.status != 'Завершена':
            self.status = 'Завершена'
            self.save()
            # Вычитаем товар из наличия только если ещё не вычли
            if not self.order.stock_deducted:
                for book in self.order.book.all():
                    book.stock -= 1
                    book.save()
                # Отмечаем что товар был вычтен
                self.order.stock_deducted = True
                self.order.save()
    

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