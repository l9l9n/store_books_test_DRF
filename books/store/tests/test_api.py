from django.db.migrations import serializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.book_1 = Book.objects.create(name='Test book 1', price=10, author='Author 1')
        self.book_2 = Book.objects.create(name='Test book 2', price=20, author='Author 2')
        self.book_3 = Book.objects.create(name='Test book Author 1', price=30, author='Author 3')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BookSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BookSerializer([self.book_1, self.book_3], many=True).data
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
