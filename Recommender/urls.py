from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('rate_movie/', views.rate_movie, name='rate_movie'),
    path('get_recommendation/', views.get_recommendation, name='get_recommendation'),

]