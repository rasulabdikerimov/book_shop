from django import forms
from shop.models import Book, Review, CustomUser, Genres, Authors, Languages, Countries


class AdminBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'slug',
            'title', 'description', 'pub_date', 'price', 'photo',
            'genres', 'languages', 'authors'
        ]
        widgets = {
            'slug': forms.TextInput(attrs={'readonly': 'readonly'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'genres': forms.SelectMultiple(attrs={'size': 6}),
            'languages': forms.SelectMultiple(attrs={'size': 6}),
            'authors': forms.SelectMultiple(attrs={'size': 6}),
        }


class AdminGenreForm(forms.ModelForm):
    class Meta:
        model = Genres
        fields = ['genre']
        widgets = {
            'genre': forms.TextInput(attrs={'placeholder': 'Введите название жанра'}),
        }


class AdminAuthorForm(forms.ModelForm):
    class Meta:
        model = Authors
        fields = ['full_name', 'birth_date', 'country', 'photo', 'biography']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'ФИО автора'}),
            'birth_date': forms.TextInput(attrs={'placeholder': 'Дата рождения (ДД.ММ.ГГГГ)'}),
            'biography': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Биография'}),
        }


class AdminLanguageForm(forms.ModelForm):
    class Meta:
        model = Languages
        fields = ['language']
        widgets = {
            'language': forms.TextInput(attrs={'placeholder': 'Введите название языка'}),
        }


class AdminCountryForm(forms.ModelForm):
    class Meta:
        model = Countries
        fields = ['country']
        widgets = {
            'country': forms.TextInput(attrs={'placeholder': 'Введите название страны'}),
        }


class AdminReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['stars', 'comment']
        widgets = {
            'stars': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }


class AdminUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'phone_number', 'address', 'image', 'is_active', 'is_staff']
        widgets = {
            'image': forms.ClearableFileInput(),
        }
