#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from apps.positions.models import Position
from apps.rules.models import Rule


class Notification(models.Model):
    rule = models.ForeignKey(Rule, verbose_name='правило', on_delete=models.CASCADE)
    position = models.ForeignKey(Position, verbose_name='позиция', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField('создан', auto_now_add=True)
    email_send_at = models.DateTimeField('дата отправки email', null=True, blank=True)
    email_processed_at = models.DateTimeField('email обработано', null=True, blank=True)
    sms_send_at = models.DateTimeField('дата отправки sms', null=True, blank=True)
    sms_processed_at = models.DateTimeField('sms обработано', null=True, blank=True)

    def is_send_email_changelist(self):
        return self.email_send_at is not None
    is_send_email_changelist.boolean = True
    is_send_email_changelist.short_description = 'Email'

    def is_send_sms_changelist(self):
        return self.sms_send_at is not None
    is_send_sms_changelist.boolean = True
    is_send_sms_changelist.short_description = 'SMS'

    class Meta:
        verbose_name = 'инцидент'
        verbose_name_plural = 'оповещения'

    def save(self, *args, **kwargs):
        super(Notification, self).save(*args, **kwargs)