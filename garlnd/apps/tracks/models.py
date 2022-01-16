from django.conf import settings
from django.db import models, transaction
from apps.devices.models import Device
from apps.positions.models import PositionPoint
import datetime


class Track(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)# null для того чтобы можно было просто трэк сформировать без пользователя
    title = models.CharField('название', max_length=255)
    description = models.TextField('описание', blank=True, null=True)
    device = models.ForeignKey(Device, verbose_name='устройство', null=True, blank=True, on_delete=models.SET_NULL)# null для того, чтобы можно было импортировать трэк
    source = models.CharField('источник данных', max_length=255, blank=True, null=True)
    view_password = models.CharField('пароль для просмотра', max_length=255, blank=True, null=True)
    start_date = models.DateTimeField('дата начала')
    end_date = models.DateTimeField('дата окончания')
    created_at = models.DateTimeField('создан', auto_now_add=True)

    class Meta:
        verbose_name = 'трэк'
        verbose_name_plural = 'трэки'

    def save(self, *args, **kwargs):
        if not self.pk and self.device:
            if self.source is None:
                self.source = self.device.title
            with transaction.atomic():
                super(Track, self).save(*args, **kwargs)
                from apps.positions.models import Position

                for position in Position.objects.filter(device=self.device, is_broken=False, created_at__gt=self.start_date, created_at__lte=self.end_date).order_by('id'):
                    track_position = TrackPosition()
                    track_position.track = self
                    track_position.longitude = position.longitude
                    track_position.longitude_type = position.longitude_type
                    track_position.latitude = position.latitude
                    track_position.latitude_type= position.latitude_type
                    track_position.distance = position.distance
                    track_position.speed = position.speed
                    track_position.acceleration = position.acceleration
                    track_position.duration = position.duration
                    track_position.is_broken = position.is_broken
                    track_position.created_at = position.created_at
                    track_position.save()
        else:
            super(Track, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            track_positions = TrackPosition.objects.filter(track=self)
            track_positions.delete()
            super(Track, self).delete(*args, **kwargs)

    def __str__(self):
        return f'{self.id}'

    def get_positions_count(self):
        return TrackPosition.objects.filter(track=self).count()

    def get_positions(self):
        return TrackPosition.objects.filter(track=self, is_broken=False).order_by('id')

    def is_opened(self):
        return self.view_password is None or not len(self.view_password)

    def is_opened_changelist(self):
        return self.is_opened()
    is_opened_changelist.short_description = 'Открыт'

    def get_url(self):
        return '/%d/' % self.id if self.view_password is None else '/%d/?password=%s' % (self.id, self.view_password)

    def get_url_changelist(self):
        return '<a href="%s" target="_blank">Просмотр</a>' % self.get_url()


class TrackPosition(PositionPoint):
    track = models.ForeignKey(Track, verbose_name='трек', on_delete=models.CASCADE)
    created_at = models.DateTimeField('создан', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        super(TrackPosition, self).save(*args, **kwargs)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'точка трека'
        verbose_name_plural = 'путевые точки треков'
