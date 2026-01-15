from unittest import TestCase

from django.contrib.auth.models import User

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')
        user3 = User.objects.create(username='user3')

        book_1 = Book.objects.create(name='Test book 1', price=10, author='Author 1')
        book_2 = Book.objects.create(name='Test book 2', price=20, author='Author 2')

        UserBookRelation.objects.create(user=user1, book=book_1, like=True)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True)
        UserBookRelation.objects.create(user=user3, book=book_1, like=True)

        UserBookRelation.objects.create(user=user1, book=book_2, like=True)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        data = BookSerializer([book_1, book_2], many=True).data
        # print(data)
        expected_data = [
            {
                'id': book_1.id,
                'name': "Test book 1",
                'price': "10.00",
                'author': 'Author 1',
                'like_count': 3,
            },
            {
                'id': book_2.id,
                'name': "Test book 2",
                'price': "20.00",
                'author': 'Author 2',
                'like_count': 2,
            },
        ]
        self.assertEqual(data, expected_data)