from django.conf import settings


def site_constants(request):
    return { 'SITE_NAME': settings.SITE_NAME }