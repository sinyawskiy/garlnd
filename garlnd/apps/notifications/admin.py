from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    search_fields = ('rule__title',)
    list_display = ('id', 'rule', 'position', 'is_send_sms_changelist', 'is_send_email_changelist', 'created_at')
    raw_id_fields = ('rule', 'position')
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)
    model = Notification

admin.site.register(Notification, NotificationAdmin)
