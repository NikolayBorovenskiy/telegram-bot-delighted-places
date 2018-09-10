from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def index(request):
    return HttpResponse('ok')
