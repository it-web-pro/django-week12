from django import forms
from .models import Blog
from django.contrib.auth.models import User
from category.models import Category


class BlogForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(
    ),  widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = Blog
        fields = ['title', 'content', 'categories']

