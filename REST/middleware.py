from django.utils import timezone
from .models import MyUser


class LastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            # Aktualizacja czasu ostatniej aktywności
            MyUser.objects.filter(id=request.user.id).update(last_activity=timezone.now())
        return response
