from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view()),
    path("/about", views.AboutView.as_view()),
]
