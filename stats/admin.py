from django.contrib import admin
from stats.models import Beatmap, User, Match, Game, Score

admin.site.register(Beatmap, admin.ModelAdmin)
admin.site.register(User, admin.ModelAdmin)
admin.site.register(Match, admin.ModelAdmin)
admin.site.register(Game, admin.ModelAdmin)
admin.site.register(Score, admin.ModelAdmin)
