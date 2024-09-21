from django.urls import path

from blogs.views import BlogListView, BlogDetailView, BlogCreateView, BlogEditView, BlogDeleteView

urlpatterns = [
    path("", BlogListView.as_view(), name="blog-list"),
    path("<int:pk>", BlogDetailView.as_view(), name="blog-detail"),
    path("create", BlogCreateView.as_view(), name="blog-create"),
    path("edit/<int:pk>", BlogEditView.as_view(), name="blog-edit"),
    path("delete/<int:pk>", BlogDeleteView.as_view(), name="blog-delete")
]
