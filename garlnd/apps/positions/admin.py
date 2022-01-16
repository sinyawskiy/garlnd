from django.contrib import admin
from .models import Position


class PositionAdmin(admin.ModelAdmin):
    search_fields = ('device__user',)
    list_display = ('device', 'longitude', 'latitude', 'distance', 'speed', 'acceleration', 'created_at')
    list_filter = ('is_broken',)
    raw_id_fields = ('device',)
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)
    model = Position


admin.site.register(Position, PositionAdmin)
