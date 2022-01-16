from django.contrib import admin
# from annoying.admin import EditMediaModelAdmin
# from django.conf import settings
from apps.maps.models import Map


class MapAdmin(admin.ModelAdmin):
    search_fields = ('owner__email', 'title')
    list_display = ('id', 'title', 'get_url_changelist', 'is_opened_changelist', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    list_display_links = ('id', 'title')
    model = Map

    raw_id_fields = ('owner',)

    # class EditMedia(object):
    #     css = {
    #         'all': ('css/admin_map.css',)
    #     }
    #     js = (
    #         '%sjs/admin_map.js' % settings.STATIC_URL,
    #     )

admin.site.register(Map, MapAdmin)
