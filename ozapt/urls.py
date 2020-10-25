from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    # path("players", views.PlayersView.as_view(), name="players"),
]
