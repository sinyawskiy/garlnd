# -*- coding: utf-8 -*-
import datetime
import urllib
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand
import time
import warnings
from django.db import connection
from django.db.models import Count
from django.template.context import Context
from django.template.loader import get_template
from django.conf import settings
from django.utils.encoding import iri_to_uri
from annoying.phonenumber import PhoneNumber
from notifications.models import Notification


 # context={'message_text':text,}
 #            plain_text_template = get_template('mails/sms_message.txt')
 #            plain_text = plain_text_template.render(Context(context))
 #            #phone 79500276617
 #            url='http://%s:%d/gateway/sendsms/?user=%s&password=%s&phone=%s&text=%s' \
 #            % (settings.SMS_HOST, settings.SMS_PORT, settings.SMS_LOGIN, settings.SMS_PASSWORD, person.phone_number_sms, iri_to_uri(plain_text))
 #            try:
 #                f = urllib.urlopen(url)
 #                #print(f.read())
 #                f.close()
 #            except IOError:
 #                pass


class Command(BaseCommand):
    help = 'Send notification mails and sms/n'

    def handle(self, *args, **options):

        start = time.time()
        limit_seconds = 180
        run_time = 0
        plain_text_template = get_template('sms_notification.txt')

        notification_min_id_query = '''
            SELECT MIN(`nn`.`id`) FROM `notifications_notification` `nn` WHERE `nn`.`sms_processed_at` IS NULL;
        '''
        cursor = connection.cursor()
        cursor.execute(notification_min_id_query)
        notification_min_id = cursor.fetchone()[0] or 0

        notification_max_id_query = '''
            SELECT MAX(`nn`.`id`) FROM `notifications_notification` `nn` WHERE `nn`.`sms_processed_at` IS NULL;
        '''
        cursor = connection.cursor()
        cursor.execute(notification_max_id_query)
        notification_max_id = cursor.fetchone()[0] or 0

        notifications_without_sms_phone_number_qs = Notification.objects.filter(sms_processed_at=None, rule__phone_number_sms=None, id__gte=notification_min_id, id__lte=notification_max_id)
        notifications_without_sms_phone_number_qs.update(sms_processed_at=datetime.datetime.now())

        notification_recipients_qs = Notification.objects.filter(sms_processed_at=None, id__gte=notification_min_id, id__lte=notification_max_id).values_list('rule__phone_number_sms', flat=True).order_by('created_at').annotate(dcount=Count('rule'))
        recipients_count = notification_recipients_qs.count()
        if recipients_count:
            print('Start date %s; Notifications for send %d\n' % (time.ctime(), recipients_count))
            notifications_send = 0
            for recipient in notification_recipients_qs:
                print('Recipient %s' % recipient)
                #Смотрим другие письма для данного получателя
                chain_notification_qs = Notification.objects.select_related('rule').filter(sms_processed_at=None, id__gte=notification_min_id, id__lte=notification_max_id, rule__phone_number_sms=recipient).order_by('-created_at')
                notifications_count = chain_notification_qs.count()
                if notifications_count:
                    sms_data = {
                        'notifications': chain_notification_qs,
                    }

                    sms_context = Context(sms_data)
                    sms_message = plain_text_template.render(sms_context).encode("UTF-8")

                    url = settings.SMS_URL % {
                        'to': PhoneNumber.phone_number_sms_format(recipient),
                        'text': iri_to_uri(sms_message)
                    }
                    print(url)
                    try:
                        f = urllib.urlopen(url)
                        f.close()
                    except IOError:
                        pass

                    chain_notification_qs.update(sms_send_at=datetime.datetime.now(), sms_processed_at=datetime.datetime.now())

                    #Проверяем время если больше лимита то выходим
                    notifications_send += notifications_count
                    run_time = time.time() - start

                    if run_time > limit_seconds:
                        self.stdout.write('Exit by time. SMS sent: %d\n' % notifications_send)

            self.stdout.write('Successfull. SMS sent: %d. Time %s \n' % (notifications_send, run_time, ))
        else:
            self.stdout.write('Start date %s;Not sms. Successful!\n' % time.ctime())