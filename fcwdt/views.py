from django.conf import settings
from django.forms import model_to_dict
from django.urls import reverse, NoReverseMatch
from django.views.generic import TemplateView, ListView, DetailView

from osu_tournament_site.utils import template_exists
from stats import models
from stats.models import MOD_ORDER

INDEX_TEMPLATE_NAME = "fcwdt/index.html"
ABOUT_TEMPLATE_NAME = "fcwdt/about.html"

DOWNLOAD_LINKS = {
    "Semi Finals": {
        "Div1": "http://www.mediafire.com/file/athzo95m5n1o0b1/Div1+SemiFinals.rar/file",
        "Div2": "http://www.mediafire.com/file/o8yplohp8byg0e0/Div2+SemiFinals.rar/file"
    }
}


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
    context['divisions'] = models.Division.objects.all().order_by('name')


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
        context["divisions"] = models.Division.objects.all().order_by("name")
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
        sdfh = []
        for mappool in models.MapPool.objects.all().order_by('-created_at'):
            divisions = []
            for division in mappool.division_set.all():
                divisions.append({
                    "name": division.name,
                    "beatmaps": sorted(
                        [beatmap.apply_mod() for beatmap in mappool.beatmap_set.filter(division=division)],
                        key=lambda x: (MOD_ORDER[x.mod], x.identifier)
                    )
                })
            sdfh.append({
                **model_to_dict(mappool),
                "beatmaps": mappool.beatmaps,
                "divisions": divisions
            })
        return sdfh

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_nav_urls_to_context(context)
        return context


class DivisionMapPoolView(DetailView):
    template_name = "fcwdt/division_mappool.html"
    model = models.Division
    context_object_name = 'division'
    pk_url_kwarg = "division_id"

    def get_object(self, *args, **kwargs):
        return models.Division.objects.get(pk=self.kwargs[self.pk_url_kwarg], mappools__id=self.kwargs["mappool_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_nav_urls_to_context(context)
        mappool = self.object.mappools.get(pk=self.kwargs["mappool_id"])
        context["mappool"] = {
            **model_to_dict(mappool),
            "beatmaps": sorted(
                [beatmap.apply_mod() for beatmap in mappool.beatmap_set.filter(division=self.object)],
                key=lambda x: (MOD_ORDER[x.mod], x.identifier)
            )
        }
        context["division_pool_download_url"] = DOWNLOAD_LINKS.get(mappool.name, {}).get(self.object.name)
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
