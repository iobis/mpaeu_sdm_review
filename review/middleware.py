from django.shortcuts import redirect
from .models import UserAccess, SiteConfiguration
from django.shortcuts import render

# Password change middleware
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