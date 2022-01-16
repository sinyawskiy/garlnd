from django.db import models
from django.conf import settings
# from graticules.models import Graticule

from apps.devices.models import Device


class Map(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField('название', max_length=255)
    view_password = models.CharField('пароль для просмотра', max_length=255, blank=True, null=True)
    description = models.TextField('описание', blank=True, null=True)
    longitude = models.FloatField('долгота', blank=True, null=True, default=settings.DEFAULT_MAP_LONGITUDE)
    latitude = models.FloatField('широта', blank=True, null=True, default=settings.DEFAULT_MAP_LATITUDE)
    zoom = models.IntegerField('масштаб', blank=True, null=True, default=settings.DEFAULT_MAP_ZOOM)
    created_at = models.DateTimeField('создана', auto_now_add=True)
    updated_at = models.DateTimeField('изменена', auto_now=True)
    devices = models.ManyToManyField(Device, verbose_name='устройства на карте', blank=True)
    # graticules = models.ManyToManyField(Graticule, verbose_name='сетки на карте', blank=True)

    def get_devices_count(self):
        return self.devices.all().count()

    def __str__(self):
        return self.title

    def is_opened(self):
        return self.view_password is None or not len(self.view_password)

    def is_opened_changelist(self):
        return self.is_opened()
    is_opened_changelist.short_description = 'Открыта'

    def get_url(self):
        return '/%d/' % self.id if self.view_password is None else '/%d/?password=%s' % (self.id, self.view_password)

    def get_url_changelist(self):
        return '<a href="%s" target="_blank">Просмотр</a>' % self.get_url()

    get_url_changelist.allow_tags = True
    get_url_changelist.short_description = 'Ссылка'

    class Meta:
        verbose_name = 'карта'
        verbose_name_plural = 'карты'