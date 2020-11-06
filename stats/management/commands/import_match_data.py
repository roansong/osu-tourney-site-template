import os

from dateutil.parser import parse
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from pytz import UTC

from stats import models
from stats.utils import api_request


class Command(BaseCommand):
    help = 'Loads multiplayer match data'

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true', )
        parser.add_argument('--quick', action='store_true', )

    def handle(self, *args, **options):

        with open(os.path.join(settings.BASE_DIR, 'stats/beatmaplist.csv')) as f:
            pool_beatmaps = [line.split(',')[0] for line in f.readlines()[1:]]

        with open(os.path.join(settings.BASE_DIR, 'stats/multilinks.txt')) as f:
            match_ids = map(lambda x: x.strip(), f.readlines())

        if options['clean']:
            models.Score.objects.all().delete()
            models.Game.objects.all().delete()
            models.Match.objects.all().delete()
            models.Beatmap.objects.all().delete()
            models.User.objects.all().delete()
            call_command('import_beatmap_data')
            call_command('import_user_data')
        elif options['quick']:
            existing_match_ids = models.Match.objects.all().values_list('ext_id', flat=True)
            match_ids = set(match_ids) - set(existing_match_ids)
        else:
            models.Score.objects.all().delete()

        for match_id in match_ids:
            print(f"Processing match ID: {match_id}")
            api_data = api_request('get_match', {'k': settings.API_KEY, 'mp': match_id})
            match_obj = api_data.get('match', {})
            print(match_obj)
            try:
                match = models.Match.objects.get(ext_id=match_id)
                if 'qualifier' in match.name.lower():
                    match.qualifier = True
                    match.save()
            except models.Match.DoesNotExist:
                match = models.Match()
                match.ext_id = match_id
                match.name = match_obj.get('name', '')
                match.qualifier = 'qualifier' in match.name.lower()
                match_start_time = match_obj.get('start_time')
                if match_start_time:
                    match_start_time = parse(match_start_time).replace(tzinfo=UTC)
                match.start_time = match_start_time
                match_end_time = match_obj.get('end_time')
                if match_end_time:
                    match_end_time = parse(match_obj.get('end_time')).replace(tzinfo=UTC)
                match.end_time = match_end_time
                match.save()

            games_objs = api_data.get('games', [])
            for game_obj in games_objs:
                try:
                    game = models.Game.objects.get(ext_id=game_obj.get('game_id'))
                except models.Game.DoesNotExist:
                    beatmap_id = game_obj.get('beatmap_id')
                    try:
                        beatmap = models.Beatmap.objects.get(ext_id=beatmap_id)
                    except models.Beatmap.DoesNotExist:
                        beatmap_obj = api_request('get_beatmaps', {'b': beatmap_id})
                        beatmap_data = {
                            'ext_id': beatmap_id,
                            'hit_length': int(beatmap_obj.get('hit_length', 0)),
                            'total_length': int(beatmap_obj.get('hit_length', 0)),
                            'max_combo': int(beatmap_obj.get('max_combo', 0)),
                            'official': beatmap_id in pool_beatmaps
                        }
                        beatmap_data.update({
                            item: float(beatmap_obj.get(item, 0))
                            for item in [
                                'bpm',
                                'difficultyrating',
                                'diff_aim',
                                'diff_speed',
                                'diff_size',
                                'diff_overall',
                                'diff_drain',
                                'diff_approach',
                            ]
                        })
                        beatmap_data.update({
                            item: beatmap_obj.get(item)
                            for item in [
                                'beatmapset_id',
                                'title',
                                'version',
                                'artist',
                                'creator',
                                'file_md5',
                                'tags',
                            ]
                        })
                        beatmap = models.Beatmap.objects.create(**beatmap_data)

                    game = models.Game()
                    game.beatmap = beatmap
                    game.match = match
                    game.ext_id = game_obj.get('game_id')
                    game_start_time = game_obj.get('start_time')
                    if game_start_time:
                        game_start_time = parse(game_obj.get('start_time')).replace(tzinfo=UTC)
                    game.start_time = game_start_time
                    game_end_time = game_obj.get('end_time')
                    if game_end_time:
                        game_end_time = parse(game_obj.get('end_time')).replace(tzinfo=UTC)
                    game.end_time = game_end_time

                    game.play_mode = int(game_obj.get('play_mode'))
                    game.mods = int(game_obj.get('mods', 0))
                    game.scoring_type = int(game_obj.get('scoring_type'))
                    game.team_type = int(game_obj.get('team_type'))
                    game.save()

                score_objs = game_obj.get('scores', [])
                for score_obj in score_objs:
                    user_id = score_obj.get('user_id')
                    try:
                        user = models.User.objects.get(ext_id=user_id)
                    except models.User.DoesNotExist:
                        continue
                    models.Score.objects.update_or_create(
                        game=game,
                        slot=int(score_obj.get('slot', 0)),
                        team=int(score_obj.get('team', 0)),
                        user=user,
                        score=int(score_obj.get('score', 0)),
                        max_combo=int(score_obj.get('maxcombo', 0)),
                        count_50=int(score_obj.get('count50', 0)),
                        count_100=int(score_obj.get('count100', 0)),
                        count_300=int(score_obj.get('count300', 0)),
                        count_miss=int(score_obj.get('countmiss', 0)),
                        perfect=bool(score_obj.get('perfect')),
                        passed=bool(score_obj.get('pass')),
                    )
