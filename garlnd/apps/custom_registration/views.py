from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login
from django.contrib.auth.decorators import login_required
# from django.contrib.auth import password_reset, password_reset_confirm, password_change
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.sites.models import Site
from django.contrib.sites.requests import RequestSite
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView
from registration import signals
from registration.backends.default.views import RegistrationView
from .forms import CustomRegistrationForm, CustomAuthenticationForm, CustomSetPasswordForm, CustomPasswordChangeForm, CustomPasswordResetForm
from django.conf import settings
from utils.decorators import garlnd_ratelimit
from .models import CustomRegistrationProfile


class PortalRegistrationView(RegistrationView):
    form_class = CustomRegistrationForm
    template_name = 'registration/custom_registration_form.html'

    @garlnd_ratelimit(block=True)
    def post(self, request, *args, **kwargs):
        return super(PortalRegistrationView, self).post(request, *args, **kwargs)

    def register(self, request, **cleaned_data):
        email, password = cleaned_data['email'], cleaned_data['password']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = CustomRegistrationProfile.objects.create_inactive_user(email, password, site)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user


class LoginView(FormView):
    form_class = CustomAuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'login.html'
    success_url = settings.LOGIN_REDIRECT_URL

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                setattr(self.request, 'limits', {})
                return HttpResponseRedirect(self.get_success_url())
            else:
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        if self.success_url:
            redirect_to = self.success_url
        else:
            redirect_to = self.request.POST.get(self.redirect_field_name, '')
        return redirect_to

    @garlnd_ratelimit(field='email', method='POST', rate='1/m')
    def post(self, request, *args, **kwargs):

        form = self.form_class(data=self.request.POST, show_captcha=getattr(request, 'limited', False))
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class PortalPasswordChangeView(PasswordChangeView):
    title = 'Изменение пароля'
    template_name = 'custom_password_change_form.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('portal_auth_password_change_done')


class PortalPasswordResetView(PasswordResetView):
    template_name = 'custom_password_reset_form.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'registration/custom_password_reset_email.txt'
    subject_template_name = 'registration/custom_password_reset_email_subject.txt'
    success_url = reverse_lazy('portal_auth_password_reset_done')


class PortalPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('portal_auth_password_reset_done')
    template_name = 'custom_set_password_form.html'

