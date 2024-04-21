from django.shortcuts import render
from .models import Book
from unidecode import unidecode
from django.http import Http404
import random
from django.http import JsonResponse
from CheckBookAvailability import BookAvailability

def author_books(request, author_name):
    try:
        books = Book.objects.filter(author=author_name, availability=1)
    except Book.DoesNotExist:
        raise Http404("Autor nie istnieje.")

    return render(request, 'book_manager/author_books.html', {'books': books, 'author': author_name})

def genre_books_old(request, genre=None):
    # Pobranie gatunków książek
    genres = Book.objects.values_list('genre', flat=True).distinct().order_by('genre')
    available_books = []
    if genre:
        # Pobieranie dostępnych książek danego gatunku
        available_books = list(Book.objects.filter(genre=genre, availability=1))

    return render(request, 'book_manager/genre_books.html', {'genres': genres, 'books': available_books, 'selected_genre': genre})

def genre_books(request, genre=None):
    if 'check_availability' in request.GET and 'book_id' in request.GET:
        availability = get_book_availability(request)
        return JsonResponse({'availability': availability})

    genres = Book.objects.values_list('genre', flat=True).distinct().order_by('genre')
    available_books = []
    if genre:
        available_books = list(Book.objects.filter(genre=genre, availability=1))

    return render(request, 'book_manager/genre_books.html', {
        'genres': genres,
        'books': available_books,
        'selected_genre': genre
    })

def authors_list(request, letter=None):
    if 'check_availability' in request.GET and 'book_id' in request.GET:
        availability = get_book_availability(request)
        print("availability: ", availability)
        return JsonResponse({'availability': availability})

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


def random_book(request):
    random_book = Book.objects.filter(availability=1).order_by('?').first()
    return render(request, 'book_manager/random_book.html', {'random_book': random_book})


def get_book_availability(request):
    book_id = request.GET['book_id']
    book_title = Book.objects.get(id=book_id).title
    book_library_id = Book.objects.get(id=book_id).library_book_id
    availability = BookAvailability(book_title, book_library_id).get_book_availability()
    return availability
