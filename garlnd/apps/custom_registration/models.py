import hashlib
import random
from django.conf import settings
from django.template.loader import render_to_string
from registration.models import RegistrationManager, RegistrationProfile


class CustomRegistrationManager(RegistrationManager):
    def create_profile(self, user):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        username = user.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        activation_key = hashlib.sha1(salt+username).hexdigest()
        return self.create(user=user, activation_key=activation_key)


class CustomRegistrationProfile(RegistrationProfile):
    objects = CustomRegistrationManager()

    def send_activation_email(self, site):
        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site}
        subject = render_to_string('registration/activation_email_subject.txt', ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message = render_to_string('registration/activation_email.txt', ctx_dict)
        message_html = render_to_string('registration/activation_email.html', ctx_dict)
        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL, message_html)


    class Meta:
        verbose_name = 'активация'
        verbose_name_plural = 'регистрация'