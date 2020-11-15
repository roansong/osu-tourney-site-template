import sys

from django.db.models import Avg

from stats.models import Score, User, Beatmap, Match


def get_highest_score(mod=None):
    query = Score.objects.filter(game__beatmap__official=True)
    if mod:
        query = query.filter(game__beatmap__mod=mod)
    score = query.order_by('-score').first()

    return {
        'user': score.user,
        'beatmap': score.beatmap,
        'score': score,
        'match': score.game.match,
    }


def get_highest_avg_score():
    query = User.objects.filter(score__game__beatmap__official=True).annotate(
        avg_score=Avg('score__score')).order_by('-avg_score').first()
    return {
        'user': query,
        'score': int(query.avg_score),
    }


def get_closest_match(stomp=False):
    min_diff = sys.maxsize
    max_diff = 0
    min_match = None
    max_match = None
    for match in Match.objects.filter(qualifier=False):
        diffs = []
        for game in match.game_set.filter():
            if not game.score_set.exists():
                continue
            score1 = game.score_set.first()
            score2 = game.score_set.last()
            diff = abs(score2.score - score1.score)
            diffs.append(diff)
        average = sum(diffs) / len(diffs)

        if average > max_diff:
            max_diff = average
            max_match = match

        if average < min_diff:
            min_diff = average
            min_match = match

    match = min_match if not stomp else max_match
    if not match:
        return {}
    diff = min_diff if not stomp else max_diff
    user1 = match.game_set.filter(score__score__gte=0).first().score_set.first().user
    user2 = match.game_set.filter(score__score__gte=0).first().score_set.last().user

    return {
        'user1': user1,
        'user2': user2,
        'score_difference': int(diff),
        'match': match
    }


def get_biggest_stomp():
    return get_closest_match(stomp=True)
