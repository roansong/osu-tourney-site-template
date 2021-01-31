import os

from dateutil.parser import parse
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from pytz import UTC

from stats import models
from stats.utils import api_request


class Command(BaseCommand):
    help = 'Loads multiplayer match data'

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true', )
        parser.add_argument('--quick', action='store_true', )

    def handle(self, *args, **options):
        if options['clean']:
            models.Score.objects.all().delete()
            models.Game.objects.all().delete()
            models.Match.objects.all().delete()
            models.Beatmap.objects.all().delete()
            models.User.objects.all().delete()

        call_command("import_user_data")
        call_command("import_beatmap_data")
        call_command("import_match_data")
