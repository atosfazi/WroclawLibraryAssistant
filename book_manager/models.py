from django.db import models

class Book(models.Model):
    year = models.CharField(max_length=4)
    genre = models.TextField()
    book_url = models.URLField()
    title = models.TextField()
    author = models.TextField()
    tags = models.TextField()
    description = models.TextField()
    rating = models.CharField(max_length=4)
    ratings_nb = models.CharField(max_length=10)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return self.title