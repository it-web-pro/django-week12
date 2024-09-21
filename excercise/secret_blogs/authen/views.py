from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib import messages
from django.views import View


class LoginView(View):
    
    def get(self, request):
        # code here
        return render(request, 'login.html', {"form": None})
    
    def post(self, request):
        # code here
        pass


class LogoutView(View):
    
    def get(self, request):
        # code here
        pass