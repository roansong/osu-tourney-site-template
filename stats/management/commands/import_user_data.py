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

        with open(os.path.join(settings.BASE_DIR, 'stats/playerlist.txt')) as f:
            user_ids = [line.strip() for line in f.readlines()]

        print(f"Registered users: {len(user_ids)}")

        if options['clean']:
            models.Score.objects.all().delete()
            models.User.objects.all().delete()

        for user_id in user_ids:
            print(f"Processing user ID: {user_id}")
            try:
                models.User.objects.get(ext_id=user_id)
            except models.User.DoesNotExist:
                user_obj = api_request('get_user', {'k': settings.API_KEY, 'u': user_id, 'type': 'id'})
                models.User.from_json(user_obj).save()

