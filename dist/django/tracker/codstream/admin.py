from django.contrib import admin
from .models import *

class databaseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in database._meta.get_fields()]


class usersAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'username',
        'cw', 'mp',  'wz',
        'time_check_cw', 'time_check_mp', 'time_check_wz',
        'records_cw', 'records_mp', 'records_wz',
        'time_records_cw', 'time_records_mp', 'time_records_wz',
        'source_records_cw', 'source_records_mp', 'source_records_wz',
        'status', 'time_all_summary_stats_cw', 'time_all_summary_stats_mp', 'time_all_summary_stats_wz'
    )
    list_editable = (
        'cw', 'mp',  'wz',
        'records_cw', 'records_mp', 'records_wz',
        'status',
    )


class wzAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'username',
        'matchID', 'timestamp',  'map', 'mode',
        'duration', 'kills', 'deaths',
        'totalXp',
    )


class mpAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'username',
        'matchID', 'timestamp',  'map', 'mode',
        'duration', 'kills', 'deaths',
        'totalXp',
    )

class cwAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user',
        'matchID', 'timestamp',  'map', 'mode',
        'duration', 'kills', 'deaths',
        'xpAtEnd',
    )


admin.site.register(users, usersAdmin)
admin.site.register(wz, wzAdmin)
admin.site.register(mp, mpAdmin)
admin.site.register(cw, cwAdmin)
admin.site.register(database, databaseAdmin)