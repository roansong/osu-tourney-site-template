from django.db import models
from django.db.models import PROTECT, DO_NOTHING

MOD_ORDER = {
    'NM': 1,
    'HD': 2,
    'HR': 3,
    'DT': 4,
    'FM': 5,
    'TB': 6
}


class MapPool(models.Model):
    name = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    download_url = models.URLField(null=True, blank=True)

    @property
    def beatmaps(self):
        return sorted(
            [beatmap.apply_mod() for beatmap in self.beatmap_set.all()],
            key=lambda x: (MOD_ORDER[x.mod], x.identifier)
        )


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
    mod = models.CharField(max_length=2, blank=True, null=True)
    mappool = models.ForeignKey(MapPool, null=True, on_delete=DO_NOTHING)
    identifier = models.TextField(null=True, blank=True)

    @classmethod
    def from_json(cls, obj: dict):
        return cls(
            ext_id=obj.get("beatmap_id"),
            beatmapset_id=obj.get("beatmapset_id"),
            title=obj.get("title"),
            version=obj.get("version"),
            artist=obj.get("artist"),
            bpm=obj.get("bpm"),
            creator=obj.get("creator"),
            difficultyrating=obj.get("difficultyrating"),
            diff_aim=obj.get("diff_aim"),
            diff_speed=obj.get("diff_speed"),
            diff_size=obj.get("diff_size"),
            diff_overall=obj.get("diff_overall"),
            diff_drain=obj.get("diff_drain"),
            diff_approach=obj.get("diff_approach"),
            hit_length=obj.get("hit_length"),
            total_length=obj.get("total_length"),
            max_combo=obj.get("max_combo"),
            file_md5=obj.get("file_md5"),
            tags=obj.get("tags"),
        )

    def apply_mod(self):
        def calc_ms(ar):
            if ar <= 5:
                return 1200 + 120 * (5 - ar)
            return 1200 - 150 * (ar - 5)

        def calc_ar(ms):
            if ms >= 1200:
                return (ms - 1200) / 120 - 5
            return -(ms - 1200) / 150 + 5

        def calc_od_ms(od):
            return 79.5 - 6 * od

        def calc_od(ms):
            return -(ms - 79.5) / 6

        if 'HR' == self.mod:
            self.diff_size *= 1.3
            self.diff_approach = min((self.diff_approach * 1.4, 10))
            self.diff_drain = min((self.diff_drain * 1.4, 10))
            self.diff_overall = min((self.diff_overall * 1.4, 10))

        if 'DT' == self.mod:
            self.bpm *= 1.5
            self.total_length = int(self.total_length / 1.5)
            self.diff_approach = calc_ar(calc_ms(self.diff_approach) / 1.5)
            self.diff_overall = calc_od(calc_od_ms(self.diff_overall) / 1.5)
        return self

    @property
    def display_title(self):
        return f"{self.artist} - {self.title} [{self.version}]"

    @property
    def url(self):
        return f"https://osu.ppy.sh/beatmaps/{self.ext_id}"

    @property
    def cover(self):
        return f"https://assets.ppy.sh/beatmaps/{self.beatmapset_id}/covers/cover.jpg"

    @property
    def length_format(self):
        minutes = self.total_length // 60
        seconds = self.total_length % 60
        return f"{minutes}:{seconds:02}"


class Division(models.Model):
    name = models.CharField(unique=True, max_length=25)


class User(models.Model):
    ext_id = models.CharField(max_length=25, unique=True)
    username = models.CharField(max_length=30)
    country = models.CharField(max_length=2)
    country_rank = models.IntegerField()
    global_rank = models.IntegerField()
    division = models.ForeignKey(Division, on_delete=PROTECT, null=True)
    chosen_class = models.TextField(null=True, blank=True)

    @classmethod
    def from_json(cls, obj: dict):
        return cls(
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
