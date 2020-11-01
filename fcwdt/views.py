from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.views.generic import TemplateView, ListView

from osu_tournament_site.utils import template_exists
from stats import models

INDEX_TEMPLATE_NAME = "fcwdt/index.html"
ABOUT_TEMPLATE_NAME = "fcwdt/about.html"


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
    exc(settings.BRACKET_URL, "bracket")
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
    template_name = "fcwdt/players.html"
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


class MapPoolView(ListView):
    template_name = "fcwdt/mappool.html"
    model = models.MapPool
    context_object_name = 'mappools'

    def get_queryset(self):
        return models.MapPool.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_nav_urls_to_context(context)
        context['maps'] = {}
        return context


class BracketView(TemplateView):
    template_name = "fcwdt/bracket.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_nav_urls_to_context(context)
        return context


class AboutView(TemplateView):
    template_name = "fcwdt/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_nav_urls_to_context(context)
        return context
