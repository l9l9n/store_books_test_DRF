import json

from django.contrib.auth.models import User
from django.db.migrations import serializer
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='9900')
        self.book_1 = Book.objects.create(name='Test book 1', price=10, author='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=20, author='Author 2', owner=self.user)
        self.book_3 = Book.objects.create(name='Test book Author 1', price=30, author='Author 3', owner=self.user)

        UserBookRelation.objects.create(user=self.user, book=self.book_1, like=True, rate=5)

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(
            annotated_like=Count(Case(When(
                userbookrelation__like=True, then=1))),
                rating = Avg('userbookrelation__rate')
        ).order_by('id')
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['like_count'], 1)
        self.assertEqual(serializer_data[0]['annotated_like'], 1)

    def test_get_search(self):
        url = reverse('book-list')
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_like=Count(Case(When(
                userbookrelation__like=True, then=1))),
                rating = Avg('userbookrelation__rate')
        ).order_by('id')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering_asc(self):
        url = reverse('book-list') + '?ordering=price'
        response = self.client.get(url)
        # print(response.data)
        prices = [item['price'] for item in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(prices, ['10.00', '20.00', '30.00'])

    def test_get_ordering_desc(self):
        url = reverse('book-list') + '?ordering=-price'
        response = self.client.get(url)
        prices = [item['price'] for item in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(prices, ['30.00', '20.00', '10.00'])

    def test_get_ordering_author(self):
        url = reverse('book-list') + '?ordering=author'
        response = self.client.get(url)
        # print(response.data)
        authors = [item['author'] for item in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(authors, ['Author 1', 'Author 2', 'Author 3'])

    def test_create(self):
        self.assertEqual(Book.objects.all().count(), 3)
        url = reverse('book-list')
        data = {
            'name': 'The Test Book 1',
            'price': '20.00',
            'author': 'Author test'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.all().count(), 4)
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': '575',
            'author': self.book_1.author
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_update_not_owner(self):
        self.user2 = User.objects.create_user(username='admin2', password='9999')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': '575',
            'author': self.book_1.author
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')}, response.data)
        self.book_1.refresh_from_db()
        self.assertEqual(10, self.book_1.price)

    def test_update_not_owner_but_stuff(self):
        self.user2 = User.objects.create_user(username='admin2', password='9999', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': '575',
            'author': self.book_1.author
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_delete(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # объект реально удалён
        self.assertFalse(Book.objects.filter(id=self.book_1.id).exists())
        # повторный GET запрос на 404
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND)


class BooksRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='9900')
        self.user2 = User.objects.create_user(username='admin2', password='9900')

        self.book_1 = Book.objects.create(name='Test book 1', price=10, author='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=20, author='Author 2', owner=self.user)

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'like': True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.like)

        data = {
            'in_bookmark': True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.in_bookmark)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'rate': 3,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(3, relation.rate)
