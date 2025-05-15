from django.urls import path
from django.contrib.auth import views as auth_views

from review.views import evaluate_next_species, species_overview

urlpatterns = [
    path("evaluate/", evaluate_next_species, name="evaluate_next_species"),
    path("dashboard/", species_overview, name="dashboard"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout')
]