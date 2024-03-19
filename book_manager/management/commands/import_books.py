from django.core.management.base import BaseCommand
import json
from book_manager.models import Book

class Command(BaseCommand):
    help = 'Imports books from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The JSON file path')

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['json_file']
        with open(json_file_path, 'r', encoding='utf-8') as file:
            books_data = file.readlines()

        for book_data in books_data:
            line = json.loads(book_data)
            Book.objects.create(
                year=line['Year'],
                genre=line['Genre'],
                book_url=line['BookUrl'],
                title=line['Title'].strip(),
                author=line['Author'].strip(),
                tags=line['Tags'],
                description=line['Description'].strip(),
                rating=line['Rating'].strip(),
                ratings_nb=line['RatingsNb'].strip(),
                availability=bool(line['Availability'])
            )

        self.stdout.write(self.style.SUCCESS('Successfully imported books from JSON'))