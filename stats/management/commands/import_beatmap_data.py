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
    'FM': 0,
    'TB': 0,
}

DOWNLOAD_LINKS = {
    'Qualifiers': "http://www.mediafire.com/file/0m2n26wid8941ze/FCWDT_Qualifiers.rar/file",
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
            previous_pool = ""
            for row in reader:
                if row['mod'] != mod or previous_pool != row['pool']:
                    map_number = 1
                try:
                    beatmap = models.Beatmap.objects.get(ext_id=row['id'])
                except models.Beatmap.DoesNotExist:
                    params = {'k': settings.API_KEY, 'b': row['id']}
                    beatmap_obj = api_request('get_beatmaps', params)
                    beatmap = models.Beatmap.from_json(beatmap_obj)

                    if row['mod'] in ['HR', 'DT']:
                        params['mods'] = MODS[row['mod']]
                        obj = api_request('get_beatmaps', params)
                        beatmap.difficultyrating = obj.get('difficultyrating')

                beatmap.mod = row['mod']
                beatmap.official = True
                beatmap.identifier = f"{beatmap.mod}{map_number}"

                mappool, _ = models.MapPool.objects.update_or_create(
                    name=row['pool'], defaults={'download_url': DOWNLOAD_LINKS.get(row['pool'])}
                )
                beatmap.mappool = mappool
                previous_pool = mappool.name

                if row['division']:
                    division, _ = models.Division.objects.get_or_create(name=row['division'])
                    division.mappools.add(mappool)
                    division.save()
                    beatmap.division = division

                beatmap.save()
                map_number += 1
                mod = row['mod']
