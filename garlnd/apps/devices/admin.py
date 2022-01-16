from django.contrib import admin
from apps.devices.forms import DeviceAdminForm
from .models import Device


def set_device_offline(modeladmin, request, queryset):
    for item in queryset:
        item.connection_address = None
        item.save()
set_device_offline.short_description = 'Установить устройство offline'


class DeviceAdmin(admin.ModelAdmin):
    search_fields = ('id', 'title')
    list_display = ('__str__', 'add_position_password', 'description_changelist', 'connection_address')
    raw_id_fields = ('owner',)
    actions = [set_device_offline, ]
    model = Device
    form = DeviceAdminForm


admin.site.register(Device, DeviceAdmin)
