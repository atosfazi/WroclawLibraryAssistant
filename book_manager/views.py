from django.shortcuts import render
from .models import Book
from random import sample
from unidecode import unidecode
from django.http import Http404

def author_books(request, author_name):
    try:
        books = Book.objects.filter(author=author_name, availability=1)
    except Book.DoesNotExist:
        raise Http404("Autor nie istnieje.")

    return render(request, 'book_manager/author_books.html', {'books': books, 'author': author_name})

def genre_books(request, genre=None):
    # Pobranie gatunków książek
    genres = Book.objects.values_list('genre', flat=True).distinct().order_by('genre')

    books = []
    if genre:
        # Pobieranie dostępnych książek danego gatunku
        available_books = list(Book.objects.filter(genre=genre, availability=1))
        # Losowe wybranie do 15 książek z listy
        books = sample(available_books, min(len(available_books), 15))

    return render(request, 'book_manager/genre_books.html', {'genres': genres, 'books': books, 'selected_genre': genre})


def authors_list(request, letter=None):
    authors = Book.objects.filter(availability=1).values_list('author', flat=True).distinct().order_by('author')

    # Generowanie listy początkowych liter autorów
    initials = set(unidecode(author[0].upper()) for author in authors if author)
    initials = sorted(list(initials))

    if letter:
        authors = [author for author in authors if unidecode(author[0].upper()) == letter]

    return render(request, 'book_manager/authors_list.html',
                  {'authors': authors, 'initials': initials, 'selected_letter': letter})

def top_books(request):
    genres = Book.objects.values_list('genre', flat=True).distinct()
    books = Book.objects.filter(availability=1).order_by('-rating')[:10]
    books_per_genres = {}

    for genre in genres:
        books_in_genre = Book.objects.filter(genre=genre, availability=1).order_by('-rating')[:15]
        books_per_genres[genre] = books_in_genre

    return render(request, 'book_manager/top_books.html', {'books': books, 'genres': genres, 'books_per_genres': books_per_genres})