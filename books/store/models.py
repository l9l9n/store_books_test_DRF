from django.contrib.auth.models import User
from django.db import models

class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author = models.CharField(max_length=255, default='')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='owner', null=True)

    def __str__(self):
        return f'Id {self.id}: {self.name}'