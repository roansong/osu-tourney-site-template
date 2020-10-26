from django.conf import settings
from django.db.models import QuerySet
from django.urls import reverse, NoReverseMatch
from django.views.generic import TemplateView, ListView

from osu_tournament_site.utils import template_exists
from stats import models

INDEX_TEMPLATE_NAME = "index.html"
ABOUT_TEMPLATE_NAME = "about.html"


def add_nav_urls_to_context(context):
    def exc(setting, name):
        try:
            context[f'{name}_url'] = setting or reverse(name)
        except NoReverseMatch:
            pass

    exc(settings.HOME_URL, "home")
    exc(settings.ABOUT_URL, "about")
    exc(settings.MAPPOOL_URL, "mappool")
    exc(settings.SCHEDULE_URL, "schedule")
    exc(settings.TEAMS_URL, "teams")
    exc(settings.PLAYERS_URL, "players")
    context['master_sheet_url'] = settings.MASTER_SHEET_URL


class IndexView(TemplateView):
    template_name = "default/index.html"

    def __init__(self):
        super().__init__()
        if template_exists(INDEX_TEMPLATE_NAME):
            self.template_name = INDEX_TEMPLATE_NAME

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_nav_urls_to_context(context)
        return context


class PlayersView(ListView):
    template_name = "players.html"
    context_object_name = "players"
    object = models.User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_nav_urls_to_context(context)
        return context

    def get_queryset(self):
        users = list(models.User.objects.all())
        users = sorted(users, key=lambda user: user.tournament_rank, reverse=True)
        users = sorted(users, key=lambda user: user.username.lower())
        return users


MOD_ORDER = {
    'NM': 1,
    'HD': 2,
    'HR': 3,
    'DT': 4,
    'FM': 5,
}


class MapPoolView(ListView):
    template_name = "mappool.html"
    model = models.MapPool
    context_object_name = 'mappool'

    def get_queryset(self):
        return models.MapPool.objects.all().order_by('-created_at').first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_nav_urls_to_context(context)
        context['maps'] = {}
        context['beatmaps'] = sorted(
            [beatmap.apply_mod() for beatmap in self.get_queryset().beatmap_set.all()],
            key=lambda x: MOD_ORDER[x.mod]
        )
        return context
