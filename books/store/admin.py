from django.contrib import admin

from store.models import Book, UserBookRelation


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'author', 'owner', 'id')
    # search_fields = ('title', 'name')

@admin.register(UserBookRelation)
class UserBookRelationAdmin(admin.ModelAdmin):
    list_display = ('book', 'rate', 'like', 'in_bookmark', 'user')