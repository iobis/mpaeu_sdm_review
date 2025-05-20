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
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]