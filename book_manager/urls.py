from django.urls import path
from .views import genre_books, authors_list, author_books, top_books

urlpatterns = [
    path('authors/', authors_list, name='authors_list'),
    path('authors/<str:letter>/', authors_list, name='authors_list'),
    path('authors/books/<str:author_name>/', author_books, name='author_books'),
    path('top/', top_books, name='top_books'),
    path('', genre_books, name='genre_books'),
    path('<str:genre>/', genre_books, name='genre_books'),
]