from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from utils.phonenumber import sms_phone_validator, PhoneNumber
from apps.devices.models import Device
from django.utils.timezone import get_current_timezone
import datetime


class RulesTypesEnum(object):
    GEO_ZONE_OUT = 1 #Выход из Гео-зоны
    GEO_ZONE_IN = 2 #Вход в Гео-зону
    DRIVE_START = 3 #Начало движения
    MAX_SPEED = 4 #Максимальная скорость
    DISCONNECT = 5 #Отключние трэкера
    CONNECT = 6 #Включение трэкера

    @classmethod
    def choices(cls):
        return (
            (cls.GEO_ZONE_OUT, cls.type_to_name(cls.GEO_ZONE_OUT)),
            (cls.GEO_ZONE_IN, cls.type_to_name(cls.GEO_ZONE_IN)),
            (cls.DRIVE_START, cls.type_to_name(cls.DRIVE_START)),
            (cls.MAX_SPEED, cls.type_to_name(cls.MAX_SPEED)),
            (cls.DISCONNECT, cls.type_to_name(cls.DISCONNECT)),
            (cls.CONNECT, cls.type_to_name(cls.CONNECT))
        )

    @classmethod
    def type_to_name(cls, rule_type):
        if rule_type == cls.GEO_ZONE_OUT:
            return 'Гео-зона (выход)'
        elif rule_type == cls.GEO_ZONE_IN:
            return 'Гео-зона (вход)'
        elif rule_type == cls.DRIVE_START:
            return 'Начало движения'
        elif rule_type == cls.MAX_SPEED:
            return 'Максимальная скорость'
        elif rule_type == cls.DISCONNECT:
            return 'Пропала связь'
        elif rule_type == cls.CONNECT:
            return 'Связь установлена'
        return 'Неизвестный тип'


class Rule(models.Model, PhoneNumber):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField('название правила', blank=True, null=True, max_length=255)
    description = models.TextField('описание', blank=True, null=True)
    email = models.EmailField('email для извещений', max_length=255, blank=True, null=True)
    phone_number_sms = models.CharField('номер для СМС', max_length=255, validators=(sms_phone_validator,), blank=True, null=True)
    device = models.ForeignKey(Device, verbose_name='устройство', null=True, blank=True, on_delete=models.SET_NULL)
    rule_type = models.PositiveIntegerField('тип правила', choices=RulesTypesEnum.choices())
    max_speed = models.FloatField('порог скорости (км/ч)', blank=True, null=True)
    initial_longitude = models.FloatField('долгота (градусы)', null=True, blank=True)
    initial_latitude = models.FloatField('широта (градусы)', null=True, blank=True)
    distance_offset = models.FloatField('радиус зоны (км)', validators=[MinValueValidator(0.025), MaxValueValidator(25)], blank=True, null=True)
    auto_reactivate = models.BooleanField('авто активация', default=False, help_text='После срабатывания активируется вновь')
    is_active = models.BooleanField('активно', default=True)
    activated_at = models.DateTimeField('дата активации', null=True, blank=True)
    deactivated_at = models.DateTimeField('дата деактивации', null=True, blank=True)
    created_at = models.DateTimeField('создан', auto_now_add=True)

    class Meta:
        verbose_name = 'правило'
        verbose_name_plural = 'правила'

    def __str__(self):
        return f'{self.id}'

    def get_rule_type_title(self):
        return RulesTypesEnum.type_to_name(self.rule_type)

    def get_count_notifications(self):
        from apps.notifications.models import Notification
        return Notification.objects.filter(rule=self).count()

    def save(self, *args, **kwargs):
        if self.id:
            before_rule = Rule.objects.get(id=self.id)
            if before_rule.is_active and not self.is_active:
                self.deactivated_at = datetime.datetime.now().replace(tzinfo=get_current_timezone())
                self.activated_at = self.activated_at.replace(tzinfo=get_current_timezone())

            elif not before_rule.is_active and self.is_active:
                self.activated_at = datetime.datetime.now().replace(tzinfo=None)
                self.deactivated_at = None
        else:
            if self.is_active:
                self.activated_at = datetime.datetime.now().replace(tzinfo=get_current_timezone())

        if self.phone_number_sms is not None:
            self.phone_number_sms = self.phone_number_base_format(self.phone_number_sms)

        # ac = self.activated_at.replace(tzinfo=None)
        # de = self.deactivated_at.replace(tzinfo=None)
        super(Rule, self).save(*args, **kwargs)


    def get_last_fire_date(self):
        from apps.notifications.models import Notification
        notifications_qs = Notification.objects.filter(rule=self).order_by('-id')[:1]
        if notifications_qs.count():
            return notifications_qs[0].created_at
        else:
            return None

