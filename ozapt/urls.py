from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("/about", views.AboutView.as_view(), name="about"),
]
