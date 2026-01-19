from django.contrib.auth.models import User
from django.db.models import F
from rest_framework import serializers

from store.models import Book, UserBookRelation


class BookReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class BookSerializer(serializers.ModelSerializer):
    annotated_like = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True, default='')
    readers = BookReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author', 'annotated_like', 'rating', 'owner_name', 'readers')


class UserBookRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmark', 'rate')