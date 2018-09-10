from django.conf import settings
from django.conf.urls import url

from .views import webhook

urlpatterns = [
    url(r'{}$'.format(settings.TELEGRAM_TOKEN), webhook),
]
