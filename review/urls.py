from django.urls import path
from django.contrib.auth import views as auth_views
from review.views import evaluate_next_species, species_overview, evaluate_species, evaluation_complete, force_password_change
from django.views.generic import TemplateView

urlpatterns = [
    path("evaluate/", evaluate_next_species, name="evaluate_next_species"),
    path("dashboard/", species_overview, name="dashboard"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('evaluate/<str:species_key>/', evaluate_species, name='evaluate_species'),
    path('done/<str:user_code>/', evaluation_complete, name='evaluation_complete'),
    path('force-password-change/', force_password_change, name='force_password_change'),
    path('help/', TemplateView.as_view(template_name='help.html'), name='help'),
]