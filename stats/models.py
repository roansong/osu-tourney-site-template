from django.db import models
from django.db.models import PROTECT


class Beatmap(models.Model):
    ext_id = models.CharField(max_length=25, unique=True)
    beatmapset_id = models.CharField(max_length=25)
    title = models.TextField()
    version = models.TextField()
    artist = models.TextField()
    bpm = models.FloatField()
    creator = models.TextField()
    difficultyrating = models.FloatField()
    diff_aim = models.FloatField()
    diff_speed = models.FloatField()
    diff_size = models.FloatField()
    diff_overall = models.FloatField()
    diff_drain = models.FloatField()
    diff_approach = models.FloatField()
    hit_length = models.IntegerField()
    total_length = models.IntegerField()
    max_combo = models.IntegerField()
    file_md5 = models.TextField()
    tags = models.TextField()
    official = models.BooleanField(default=False)

    @property
    def display_title(self):
        return f"{self.artist} - {self.title} [{self.version}]"

    @property
    def url(self):
        return f"https://osu.ppy.sh/beatmaps/{self.ext_id}"


class Division(models.Model):
    name = models.CharField(unique=True, max_length=25)


class User(models.Model):
    ext_id = models.CharField(max_length=25, unique=True)
    username = models.CharField(max_length=30)
    country = models.CharField(max_length=2)
    country_rank = models.IntegerField()
    global_rank = models.IntegerField()
    division = models.ForeignKey(Division, on_delete=PROTECT, null=True)

    @classmethod
    def from_json(cls, obj: dict):
        return User(
            username=obj.get('username'),
            ext_id=obj.get('user_id'),
            global_rank=obj.get('pp_rank'),
            country_rank=obj.get('pp_country_rank'),
            country=obj.get('country'),
        )

    @property
    def profile_url(self):
        return f"https://osu.ppy.sh/users/{self.ext_id}"

    @property
    def acc(self):
        return sum([score.acc for score in self.score_set.all()]) / self.score_set.count()

    @property
    def avatar_url(self):
        return f"https://a.ppy.sh/{self.ext_id}"

    @property
    def flag_url(self):
        return f"https://osu.ppy.sh/images/flags/{self.country}.png"

    @property
    def tournament_rank(self):
        return "-"


class Match(models.Model):
    ext_id = models.CharField(max_length=25, unique=True)
    name = models.CharField(max_length=100, blank=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    qualifier = models.BooleanField(default=False)

    @property
    def url(self):
        return f"https://osu.ppy.sh/mp/{self.ext_id}"


class Game(models.Model):
    ext_id = models.CharField(max_length=25, unique=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    mods = models.IntegerField()
    match = models.ForeignKey(Match, on_delete=PROTECT, null=True)
    beatmap = models.ForeignKey(Beatmap, on_delete=PROTECT, null=True)
    play_mode = models.IntegerField()
    scoring_type = models.IntegerField()
    team_type = models.IntegerField()


class Score(models.Model):
    slot = models.IntegerField()
    team = models.IntegerField()
    user = models.ForeignKey(User, on_delete=PROTECT)
    score = models.IntegerField()
    max_combo = models.IntegerField()
    count_50 = models.IntegerField()
    count_100 = models.IntegerField()
    count_300 = models.IntegerField()
    count_miss = models.IntegerField()
    perfect = models.BooleanField()
    passed = models.BooleanField()
    enabled_mods = models.IntegerField(null=True)
    game = models.ForeignKey(Game, on_delete=PROTECT, null=True)

    @property
    def acc(self):
        return 100 * (self.count_300 * 300 + self.count_100 * 100 + self.count_50 * 50) / (
                (self.count_300 + self.count_100 + self.count_50 + self.count_miss) * 300)
