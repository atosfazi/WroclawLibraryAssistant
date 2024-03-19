from django.urls import path
from . import views

urlpatterns = [
    path('', views.button_click, name='button_click'),
]