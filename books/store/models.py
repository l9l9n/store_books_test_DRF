from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author = models.CharField(max_length=255, default='')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='my_books', null=True)
    readers = models.ManyToManyField(User, related_name='books', through='UserBookRelation')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return f'Id {self.id}: {self.name}'


class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Ok'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Incredible'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmark = models.BooleanField(default=False)
    rate = models.PositiveIntegerField(choices=RATE_CHOICES, default=1)

    def __str__(self):
        return f' {self.user.username}: {self.book.name}, {self.rate}'

    def save(self, *args, **kwargs):
        from store.logic import set_rating
        creating = not self.pk
        old_rating = self.rate

        super().save(*args, **kwargs)

        new_rating = self.rate
        if creating:
            set_rating(self.book)

