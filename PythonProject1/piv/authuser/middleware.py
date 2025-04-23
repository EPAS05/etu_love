from .models import User


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_id = request.session.get('user_id')
        request.user = None

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                if user.is_active:
                    request.user = user
            except User.DoesNotExist:
                pass

        return self.get_response(request)