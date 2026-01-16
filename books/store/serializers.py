from django.db.models import F
from rest_framework import serializers

from store.models import Book, UserBookRelation


class BookSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    annotated_like = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author', 'like_count', 'annotated_like', 'rating')


    def get_like_count(self, instance):
        return UserBookRelation.objects.filter(book=instance, like=True).count()

    # def get_annotated_like(self, instance):
    #     return getattr(instance, 'annotated_like', 0)

class UserBookRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmark', 'rate')