from django import forms
from shop.models import Book, Review, CustomUser


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
