from captcha.fields import CaptchaTextInput, CaptchaField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from apps.custom_auth.models import CustomUser as User

class CustomRegistrationForm(forms.Form):
    required_css_class = 'required'

    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Введите логин (email)', 'class': 'span4'}), label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль', 'class': 'span4'}), label="Пароль")
    captcha = CaptchaField(widget=CaptchaTextInput(attrs={'placeholder': 'Введите код', 'class': 'span2'}), label='')

    def clean_email(self):
        if User.objects.filter(email__iexact=self.cleaned_data['email']).count():
            raise forms.ValidationError("Этот адрес уже используется. Выберите другой")
        return self.cleaned_data['email']


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Введите логин (email)', 'class': 'span4'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль', 'class': 'span4'}))

    def __init__(self, request=None, show_captcha=False, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(request, *args, **kwargs)
        if show_captcha:
            self.fields['captcha'] = CaptchaField(widget=CaptchaTextInput(attrs={'placeholder': 'Введите код', 'class': 'span2'}), label='')


class CustomSetPasswordForm(forms.Form):
    new_password = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль', 'class': 'span4'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password'])
        if commit:
            self.user.save()
        return self.user


class CustomPasswordChangeForm(CustomSetPasswordForm):
    error_messages = {
        'password_incorrect': "Ваш пароль введен некорректно. Повторите пожалуйста",
    }
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль', 'class': 'span4'}))

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'])
        return old_password

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Введите логин (email)', 'class': 'span4'}), label="Email", max_length=254)
    captcha = CaptchaField(widget=CaptchaTextInput(attrs={'placeholder': 'Введите код', 'class': 'span2'}), label='')

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.txt',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, email_html_template_name='registration/custom_password_reset_email.html'):

        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        active_users = UserModel._default_manager.filter(
            email__iexact=email, is_active=True)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            message = loader.render_to_string(email_template_name, c)
            message_html = loader.render_to_string(email_html_template_name, c) if email_html_template_name else None
            user.email_user(subject, message, from_email, message_html)