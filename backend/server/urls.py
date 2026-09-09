from django.urls import path
from . import views

#URL Configuration
urlpatterns = [
    path('rungmail', views.dashboard),
    path('dashboard', views.dashboard),
    path('dashboard/summary', views.summary),
    path('dashboard/review', views.review_queue),
    path('exports/training', views.export_training_data),
    path('actions/apply', views.apply_actions),
]
