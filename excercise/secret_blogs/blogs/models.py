from django.db import models
from django.contrib.auth.models import User
from category.models import Category

class Blog(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)
    
    def __str__(self):
        return "{title} by {username}".format(title=self.title, username=self.author.username)
    
    def get_str_categorise(self):
        cate_list = self.categories.values_list("name", flat=True)
        joined_string_comma = ', '.join([item for item in cate_list])
        return joined_string_comma
        
