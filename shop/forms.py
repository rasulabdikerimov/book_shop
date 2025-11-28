from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import CustomUser,Review, Book


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'address', 'image')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'address', 'image')

class ReviewForm(forms.ModelForm):
    stars = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Review
        fields = ['stars', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Поделитесь вашими впечатлениями...',
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-600 focus:outline-none resize-none dark:bg-slate-700 dark:border-slate-600 dark:text-white'
            })
        }

