from django.shortcuts import redirect
from .models import UserAccess

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                access = UserAccess.objects.get(user_code=request.user.username)
                if access.must_change_password and request.path != '/force-password-change/':
                    return redirect('force_password_change')
            except UserAccess.DoesNotExist:
                pass

        response = self.get_response(request)  # Call next middleware/view
        return response
