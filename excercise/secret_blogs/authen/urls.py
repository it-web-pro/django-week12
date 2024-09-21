from django.urls import path

from authen.views import LoginView, LogoutView


urlpatterns = [
    path('', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout")
]