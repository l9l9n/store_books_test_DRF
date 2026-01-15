from unittest import TestCase

from store.models import Book
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = Book.objects.create(name='Test book 1', price=10, author='Author 1')
        book_2 = Book.objects.create(name='Test book 2', price=20, author='Author 2')
        data = BookSerializer([book_1, book_2], many=True)
        expected_data = [
            {
                'id': book_1.id,
                'name': "Test book 1",
                'price': "10.00",
                'author': 'Author 1'
            },
            {
                'id': book_2.id,
                'name': "Test book 2",
                'price': "20.00",
                'author': 'Author 2'
            },
        ]
        self.assertEqual(data.data, expected_data)