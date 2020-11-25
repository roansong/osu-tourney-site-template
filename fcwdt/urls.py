from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("players", views.PlayersView.as_view(), name="players"),
    path("mappool", views.MapPoolView.as_view(), name="mappool"),
    path("division/<int:division_id>/mappool/<int:mappool_id>", views.DivisionMapPoolView.as_view(), name="division_mappool"),
    path("info", views.AboutView.as_view(), name="about"),
    # path("bracket", views.BracketView.as_view(), name="bracket"),
]
