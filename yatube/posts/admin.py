from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    DISPLAY_SCREEN = '-пусто-'
    list_editable = ('group',)
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = DISPLAY_SCREEN
