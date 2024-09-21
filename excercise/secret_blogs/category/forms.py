from django.forms import ModelForm
from category.models import Category


class CategoryModelForm(ModelForm):
    
    class Meta:
        model = Category
        fields = [
            "name",
            "color"
        ]
    