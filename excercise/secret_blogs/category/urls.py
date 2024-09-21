from django.urls import path

from category.views import CategoryListView, CategoryCreateView, CategoryEditView, CategoryDeleteView


urlpatterns = [
    path('', CategoryListView.as_view(), name="category-list"),
    path('create', CategoryCreateView.as_view(), name="category-create"),
    path('edit/<int:pk>', CategoryEditView.as_view(), name="category-edit"),
    path('delete/<int:pk>', CategoryDeleteView.as_view(), name="category-delete")
]