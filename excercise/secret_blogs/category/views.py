from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib import messages
from category.models import Category
from category.forms import CategoryModelForm


class CategoryListView(View):
    
    def get(self, request: HttpRequest):
        category_qs = Category.objects.all()
        
        form_category_list = [
            CategoryModelForm(instance=category)
            for category in category_qs
        ]
        context = {
            "forms": form_category_list,
            "category_qs": category_qs
        }
        
        return render(request, "list_category.html", context)
    

class CategoryCreateView(View):
    
    def post(self, request: HttpRequest):
        form = CategoryModelForm(request.POST)
        
        if form.is_valid():
            form.save()
        else:
            non_field_errors_mes = str(form.non_field_errors())
            messages.error(request, "create error {error}".format( error=non_field_errors_mes ))
            
        return redirect('category-list')
        

class CategoryEditView(View):
    
    def post(self, request: HttpRequest, pk):
        category = get_object_or_404(Category, pk=pk)
        form = CategoryModelForm(request.POST, instance=category)
        
        if form.is_valid():
            form.save()
            
        return redirect('category-list')


class CategoryDeleteView(View):
    
    def get(self, request: HttpRequest, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return redirect('category-list')
        