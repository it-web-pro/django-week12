from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=10, default="#FFFFFF")
    
    def __str__(self) -> str:
        return self.name