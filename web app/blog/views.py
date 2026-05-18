from django.shortcuts import render
from django.http import HttpResponse
# Create your models here.
def home(request):
    return render(request, 'blog/home.html')
# Create your views here.
def about(request):
    return render(request, 'blog/about.html' )