from django.contrib import admin
from .models import Track, TrackPosition


class TrackAdmin(admin.ModelAdmin):
    search_fields = ('id', 'title')
    list_display = ('__str__', 'get_url_changelist', 'is_opened_changelist')
    raw_id_fields = ('owner',)
    model = Track


class TrackPositionAdmin(admin.ModelAdmin):
    search_fields = ('track__device__user',)
    list_display = ('track', 'longitude', 'latitude', 'distance', 'speed', 'acceleration', 'created_at',)
    list_filter = ('is_broken',)
    raw_id_fields = ('track',)
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)
    model = TrackPosition


admin.site.register(TrackPosition, TrackPositionAdmin)
admin.site.register(Track, TrackAdmin)
