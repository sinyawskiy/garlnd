# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Mark notifications as unsent/n'

    def handle(self, *args, **options):
        notifications_qs = Notification.objects.all()
        notifications_qs.update(email_send_at=None, sms_send_at=None, email_processed_at=None, sms_processed_at=None)