# -*- coding: utf-8 -*-
import datetime
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand
import time
from django.db import connection
from django.db.models import Count
from django.template.loader import get_template
from django.conf import settings
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Send notification mails and sms/n'

    def handle(self, *args, **options):

        start = time.time()
        limit_seconds = 180
        run_time = 0
        plain_text_template = get_template('email_notification.txt')
        html_template = get_template('email_notification.html')
        domain = 'garlnd.r'
        protocol = 'http'
        subject = 'Уведомление о событиях GARLND'

        notification_min_id_query = '''
            SELECT MIN(`nn`.`id`) FROM `notifications_notification` `nn` WHERE `nn`.`email_processed_at` IS NULL;
        '''
        cursor = connection.cursor()
        cursor.execute(notification_min_id_query)
        notification_min_id = cursor.fetchone()[0] or 0

        notification_max_id_query = '''
            SELECT MAX(`nn`.`id`) FROM `notifications_notification` `nn` WHERE `nn`.`email_processed_at` IS NULL;
        '''
        cursor = connection.cursor()
        cursor.execute(notification_max_id_query)
        notification_max_id = cursor.fetchone()[0] or 0

        notifications_without_email_qs = Notification.objects.filter(email_processed_at=None, rule__email=None, id__gte=notification_min_id, id__lte=notification_max_id)
        notifications_without_email_qs.update(email_processed_at=datetime.datetime.now())

        notification_recipients_qs = Notification.objects.filter(email_processed_at=None, id__gte=notification_min_id, id__lte=notification_max_id).values_list('rule__email', flat=True).order_by('created_at').annotate(dcount=Count('rule'))
        recipients_count = notification_recipients_qs.count()
        if recipients_count:
            print('Start date %s; Notifications for send %d\n' % (time.ctime(), recipients_count))
            notifications_send = 0
            for recipient in notification_recipients_qs:
                print('Recipient %s' % recipient)
                #Смотрим другие письма для данного получателя
                chain_notification_qs = Notification.objects.filter(email_processed_at=None, id__gte=notification_min_id, id__lte=notification_max_id, rule__email=recipient).select_related('rule', 'position').order_by('-created_at')
                notifications_count = chain_notification_qs.count()
                if notifications_count:
                    mail_data = {
                        'notifications': chain_notification_qs,
                        'domain': domain,
                        'protocol': protocol
                    }

                    text_message = plain_text_template.render(mail_data).encode("UTF-8")
                    html_message = html_template.render(mail_data).encode("UTF-8")

                    msg = EmailMultiAlternatives(subject, text_message, settings.EMAIL_ADDRESS_FROM, [recipient,],[], headers={'X-Priority':'2'})
                    self.stdout.write('Attach alternative HTML\n')
                    msg.attach_alternative(html_message, 'text/html')

                    #Отправить
                    msg.send()
                    chain_notification_qs.update(email_send_at=datetime.datetime.now(), email_processed_at=datetime.datetime.now())

                    #Проверяем время если больше лимита то выходим
                    notifications_send += notifications_count
                    run_time = time.time() - start

                    if run_time > limit_seconds:
                        self.stdout.write('Exit by time. Mails sent: %d\n' % notifications_send)

            self.stdout.write('Successfull. Mails sent: %d. Time %s \n' % (notifications_send, run_time, ))
        else:
            self.stdout.write('Start date %s;Not mails. Successful!\n' % time.ctime())
