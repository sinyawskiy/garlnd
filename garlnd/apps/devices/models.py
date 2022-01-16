import os
import re
import string

from django.conf import settings
from django.core.validators import MaxValueValidator, RegexValidator, MinValueValidator
from django.db import models
from django.db.models.aggregates import Avg, Sum
from utils.functions import padd_to
from utils.helpers import id_generator



def device_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    pk = '%s' % id_generator(15)
    file_name = 'devices/%s%s' % (pk, ext)
    exists_path = os.path.join(settings.MEDIA_ROOT, file_name)
    while os.path.exists(exists_path):
        file_name = 'devices/%s%s' % (pk, ext)
        exists_path = os.path.join(settings.MEDIA_ROOT, file_name)
    return file_name


class Device(models.Model):
    default_color = '#c41e3a'
    default_image = 'img/map_icons/circle_green.png'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField('название устройства', blank=True, null=True, max_length=255)
    description = models.TextField('описание', blank=True, null=True)
    image = models.FileField(verbose_name='изображение', upload_to=device_upload_path, null=True, blank=True) #max_width=50, max_height=50,  format='PNG'
    add_position_password = models.CharField('идентификатор', max_length=255, unique=True, default=id_generator(5, string.ascii_uppercase), validators=[RegexValidator(regex=re.compile('^[0-9A-Z]+$'), message=''),])
    width = models.IntegerField('толщина линии (px)', default=5, validators=[MaxValueValidator(15), MinValueValidator(1)], blank=True)
    color_rgb = models.CharField('цвет линии (RGB)', default=default_color, null=True, blank=True, max_length=255)
    connection_address = models.CharField('адрес подключения', blank=True, null=True, max_length=255)
    created_at = models.DateTimeField('создан', auto_now_add=True)

    def get_device_positions_count(self):
        from apps.positions.models import Position
        return Position.objects.filter(device=self).count()

    def get_full_time(self):
        from apps.positions.models import Position
        duration = Position.objects.filter(device=self, is_broken=False).aggregate(Sum('duration'))['duration__sum']
        days, temp = divmod(duration, 3600*24)
        hours, temp = divmod(temp, 3600)
        minutes, seconds = divmod(temp, 60)
        return '%d дн. %s:%s:%s' % (days, padd_to('%d' % hours, 2), padd_to('%d' % minutes, 2), padd_to('%d' % seconds, 2)) if days else '%s:%s:%s' % (padd_to('%d' % hours,2), padd_to('%d' % minutes,2), padd_to('%d' % seconds,2))

    def get_average_speed(self):
        from apps.positions.models import Position
        return Position.objects.filter(device=self, is_broken=False).aggregate(Avg('speed'))['speed__avg'] or 0

    def get_full_distance(self):
        from apps.positions.models import Position
        return Position.objects.filter(device=self, is_broken=False).aggregate(Sum('distance'))['distance__sum'] or 0

    def is_connected(self):
        return 'Online' if self.connection_address else 'Offline'

    def description_changelist(self):
        return self.description[0:30] if self.description else '-'
    description_changelist.short_description = 'Описание (30 симв.)'

    def get_count_notifications(self, rule_type=None):
        from apps.notifications.models import Notification
        if rule_type is None:
            return Notification.objects.filter(rule__device=self).count()
        else:
            return Notification.objects.filter(rule__device=self, rule__rule_type=rule_type).count()

    def __str__(self):
        return '%s' % self.title if self.title else '%s' % self.id

    def get_color(self):
        if self.color_rgb:
            return '%s' % self.color_rgb
        else:
            return self.default_color

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return '%s%s' % (settings.STATIC_URL, self.default_image)

    def get_last_position(self):
        from apps.positions.models import Position
        device_positions = Position.objects.filter(device=self)
        return device_positions.values_list('longitude', 'latitude').order_by('-id')[:1][0] if device_positions.count() else ('','')

    def get_tracks(self):
        from apps.tracks.models import Track
        return Track.objects.filter(device=self)

    def delete(self, *args, **kwargs):
        tracks = self.get_tracks()
        tracks.update(device=None)
        super(Device, self).delete(*args, **kwargs)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'трекер'
        verbose_name_plural = 'трекеры'

