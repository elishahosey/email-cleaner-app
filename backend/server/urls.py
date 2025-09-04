from django.urls import path
from . import views

#URL Configuration
urlpatterns = [
    path('rungmail', views.run_gmail),
    path('deleteEmails',views.deleteEmail)

]