import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from stats import models
from stats.utils import api_request


class Command(BaseCommand):
    help = 'Loads user data'

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true', )
        parser.add_argument('--quick', action='store_true', )

    def handle(self, *args, **options):

        with open(os.path.join(settings.BASE_DIR, 'stats/playerlist.csv'), newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')

            if options['clean']:
                models.User.objects.all().delete()

            for row in reader:
                user_id = row['id']
                print(f"Processing user ID: {user_id}")
                try:
                    user = models.User.objects.get(ext_id=user_id)
                except models.User.DoesNotExist:
                    user_obj = api_request('get_user', {'k': settings.API_KEY, 'u': user_id, 'type': 'id'})
                    user = models.User.from_json(user_obj)

                if row['division']:
                    division, _ = models.Division.objects.get_or_create(name=row['division'])
                    user.division = division
                user.save()
