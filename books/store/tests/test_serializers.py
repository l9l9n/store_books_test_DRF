from unittest import TestCase

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='user1', first_name='Ivan', last_name='Petrov')
        user2 = User.objects.create(username='user2', first_name='Vasia', last_name='Petrov')
        user3 = User.objects.create(username='user3', first_name='Kiril', last_name='Petrov')

        book_1 = Book.objects.create(name='Test book 1', price=10, author='Author 1', owner=user1)
        book_2 = Book.objects.create(name='Test book 2', price=20, author='Author 2')

        UserBookRelation.objects.create(user=user1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=book_1, like=True, rate=4)

        UserBookRelation.objects.create(user=user1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_like=Count(Case(When(
                userbookrelation__like=True, then=1))),
                rating = Avg('userbookrelation__rate')
        ).order_by('id')

        data = BookSerializer(books, many=True).data
        # print(data)
        expected_data = [
            {
                'id': book_1.id,
                'name': "Test book 1",
                'price': "10.00",
                'author': 'Author 1',
                'annotated_like': 3,
                'rating': '4.67',
                'owner_name': 'user1',
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov',
                    },
                    {
                        'first_name': 'Vasia',
                        'last_name': 'Petrov',
                    },
                    {
                        'first_name': 'Kiril',
                        'last_name': 'Petrov',
                    },
                ],

            },
            {
                'id': book_2.id,
                'name': "Test book 2",
                'price': "20.00",
                'author': 'Author 2',
                'annotated_like': 2,
                'rating': '2.67',
                'owner_name': '',
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov',
                    },
                    {
                        'first_name': 'Vasia',
                        'last_name': 'Petrov',
                    },
                    {
                        'first_name': 'Kiril',
                        'last_name': 'Petrov',
                    },
                ],
            },
        ]
        self.assertEqual(data, expected_data)