from django.shortcuts import redirect
from .models import UserAccess, SiteConfiguration
from django.shortcuts import render

# Password change middleware
class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            if not user.is_superuser and not user.is_staff:
                try:
                    access = UserAccess.objects.get(user_code=user.username)
                    if access.must_change_password and request.path != '/force-password-change/':
                        return redirect('force_password_change')
                except UserAccess.DoesNotExist:
                    pass

        response = self.get_response(request)
        return response

# Maintenance mode middleware
class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            config = SiteConfiguration.objects.first()
            if config and config.maintenance_mode:
                # Allow staff and admin URLs
                if request.user.is_staff or request.path.startswith("/admin/"):
                    return self.get_response(request)

                return render(request, "maintenance.html", status=503)
        except Exception as e:
            print("Maintenance middleware error:", e)

        return self.get_response(request)