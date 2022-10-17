from django.core.paginator import Paginator
from django.conf import settings


def get_paginator(queryset, request):
    paginator = Paginator(queryset, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }
