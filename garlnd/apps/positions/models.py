from django.db import models
from apps.devices.models import Device

GPX_FORMAT = 1
KML_FORMAT = 2
POSITIONS_EXPORT_FORMAT_CHOICES = (
    (GPX_FORMAT, '.GPX'),
    (KML_FORMAT, '.KML')
)


class PositionPoint(models.Model):
    LONGITUDE_CHOICES = (
        ('E', 'Восточная'),
        ('W', 'Западная'),
    )
    LATITUDE_CHOICES = (
        ('N', 'Северная'),
        ('S', 'Южная'),
    )
    longitude = models.FloatField('долгота (градусы)')
    longitude_type = models.CharField('тип долготы', max_length=1, choices=LONGITUDE_CHOICES, default='N')
    latitude = models.FloatField('широта (градусы)')
    latitude_type = models.CharField('тип широты', max_length=1, choices=LATITUDE_CHOICES, default='E')
    distance = models.FloatField('расстояние (км)', blank=True, null=True)
    speed = models.FloatField('скорость (км/ч)', blank=True, null=True)
    acceleration = models.FloatField('ускорение (м/с^2)', blank=True, null=True)
    duration = models.IntegerField('время (с)', blank=True, null=True)
    is_broken = models.BooleanField('ложная точка', default=False)
    parameters = models.TextField('другие параметры', blank=True, null=True)

    def get_speed(self):
        return int(self.speed*100)/100.0 if self.speed else 0

    class Meta:
        abstract = True


class Position(PositionPoint):
    device = models.ForeignKey(Device, verbose_name='трекер', on_delete=models.CASCADE)
    created_at = models.DateTimeField('создан', auto_now_add=True)

    def __str__(self):
        return f'{self.pk}. {self.device}'

    class Meta:
        ordering = ['created_at']
        verbose_name = 'точка'
        verbose_name_plural = 'путевые точки трекеров'
