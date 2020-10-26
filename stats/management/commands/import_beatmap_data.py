import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from stats import models
from stats.utils import api_request

MODS = {
    'NM': 0,
    'EZ': 2,
    'HD': 8,
    'HR': 16,
    'DT': 64,
}

DOWNLOAD_LINKS = {
    'Qualifiers': "https://www.dropbox.com/s/yk4lfta72l6nhtl/OPTQualifiers.rar?dl=1"
}


class Command(BaseCommand):
    help = 'Loads beatmap data'

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true', )

    def handle(self, *args, **options):
        if options['clean']:
            models.Beatmap.objects.all().delete()
            models.MapPool.objects.all().delete()

        with open(os.path.join(settings.BASE_DIR, 'stats/beatmaplist.csv'), newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            map_number = 1
            mod = ""
            for row in reader:
                if row['mod'] != mod:
                    map_number = 1
                try:
                    models.Beatmap.objects.get(ext_id=row['id'])
                except models.Beatmap.DoesNotExist:
                    mappool, _ = models.MapPool.objects.get_or_create(name=row['pool'], download_url=DOWNLOAD_LINKS[row['pool']])
                    params = {'k': settings.API_KEY, 'b': row['id']}
                    beatmap_obj = api_request('get_beatmaps', params)
                    beatmap = models.Beatmap.from_json(beatmap_obj)
                    beatmap.mod = row['mod']
                    beatmap.mappool = mappool
                    beatmap.official = True
                    beatmap.identifier = f"{beatmap.mod}{map_number}"

                    if row['mod'] in ['HR', 'DT']:
                        params['mods'] = MODS[row['mod']]
                        obj = api_request('get_beatmaps', params)
                        beatmap.difficultyrating = obj.get('difficultyrating')

                beatmap.save()
                map_number += 1
                mod = row['mod']
