from math import ceil
import warnings
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import models, connection
from django.utils import timezone
# from apps.graticules.models import Graticule
# from apps.locations.models import Location, LocationType
from apps.devices.models import Device
from apps.maps.models import Map
from apps.rules.models import Rule
# from apps.schedules.models import ScheduleEvent
# from apps.statuses.models import Status
from apps.tracks.models import Track


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class SiteProfileNotAvailable(Exception):
    pass

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', max_length=255, unique=True)

    is_staff = models.BooleanField('staff status', default=False,
        help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField('active', default=True,
        help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    max_maps_count = models.PositiveIntegerField('количество карт', default=settings.DEFAULT_MAX_MAPS_COUNT, blank=True, null=True)
    # max_locations_count = models.PositiveIntegerField('количество площадок', default=settings.DEFAULT_MAX_LOCATIONS_COUNT, blank=True, null=True)
    max_devices_count = models.PositiveIntegerField('количество трэкеров', default=settings.DEFAULT_MAX_DEVICES_COUNT, blank=True, null=True)
    max_rules_count = models.PositiveIntegerField('количество правил', default=settings.DEFAULT_MAX_RULES_COUNT, blank=True, null=True)
    max_tracks_count = models.PositiveIntegerField('количество трэков', default=settings.DEFAULT_MAX_TRACKS_COUNT, blank=True, null=True)
    # max_schedule_events_count = models.PositiveIntegerField('количество событий по расписанию', default=settings.DEFAULT_MAX_SCHEDULE_EVENTS_COUNT, blank=True, null=True)
    # max_graticules_count = models.PositiveIntegerField('количество картографических сеток', default=settings.DEFAULT_MAX_GRATICULES_COUNT, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def get_maps_count(self):
        return Map.objects.filter(owner=self).count()

    def get_devices_count(self):
        return Device.objects.filter(owner=self).count()

    def get_tracks_count(self):
        return Track.objects.filter(owner=self).count()

    def get_rules_count(self):
        return Rule.objects.filter(owner=self).count()

    # def get_graticules_count(self):
    #     return Graticule.objects.filter(owner=self).count()

    def get_events_count(self):
        events_count_query = '''
        SELECT COUNT(`events_event`.`id`) FROM `maps_map` LEFT JOIN `events_event`
        ON `events_event`.`event_map_id` = `maps_map`.`id` WHERE `maps_map`.`owner_id`=%s;
        '''
        cursor = connection.cursor()
        cursor.execute(events_count_query, (self.id,))
        return cursor.fetchone()[0]

    def get_positions_count(self):
        positions_count_query = '''
        SELECT COUNT(`positions_position`.`id`) FROM `devices_device` LEFT JOIN `positions_position`
        ON `positions_position`.`device_id` = `devices_device`.`id` WHERE `devices_device`.`owner_id`=%s;
        '''
        cursor = connection.cursor()
        cursor.execute(positions_count_query, (self.id,))
        return cursor.fetchone()[0]

    def get_notifications_count(self):
        notifications_count_query = '''
        SELECT COUNT(`notifications_notification`.`id`) FROM `notifications_notification` LEFT JOIN `rules_rule`
        ON `rules_rule`.`id` = `notifications_notification`.`rule_id` WHERE `rules_rule`.`owner_id`=%s;
        '''
        cursor = connection.cursor()
        cursor.execute(notifications_count_query, (self.id,))
        return cursor.fetchone()[0]

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def email_user(self, subject, message, from_email=None, message_html=None):
        """
        Sends an email to this User.
        """
        if message_html is None:
            send_mail(subject, message, from_email, [self.email])
        else:
            msg = EmailMultiAlternatives(subject, message, from_email, [self.email])
            msg.attach_alternative(message_html, "text/html")
            msg.send()

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        warnings.warn("The use of AUTH_PROFILE_MODULE to define user profiles has been deprecated.",
            PendingDeprecationWarning)
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings
            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable(
                    'You need to set AUTH_PROFILE_MODULE in your project '
                    'settings')
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            except ValueError:
                raise SiteProfileNotAvailable(
                    'app_label and model_name should be separated by a dot in '
                    'the AUTH_PROFILE_MODULE setting')
            try:
                model = models.get_model(app_label, model_name)
                if model is None:
                    raise SiteProfileNotAvailable(
                        'Unable to load the profile model, check '
                        'AUTH_PROFILE_MODULE in your project settings')
                self._profile_cache = model._default_manager.using(
                                   self._state.db).get(user__id__exact=self.id)
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        # abstract = True
