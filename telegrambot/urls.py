from django.conf.urls import url, include

from .views import index

urlpatterns = [
    url(r'^$', index),
    url(r'^weebhook/', include('corebot.urls'))
]
