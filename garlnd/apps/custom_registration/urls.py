from django.urls import path
from django.views.generic import TemplateView
from registration.backends.default.views import ActivationView
from apps.custom_registration.views import LoginView, PortalRegistrationView, PortalPasswordResetConfirmView, PortalPasswordChangeView, PortalPasswordResetView

urlpatterns = [
    path('register/', PortalRegistrationView.as_view(), name='registration_register'),
    path('login/', LoginView.as_view(), name='login'),
    path('portal/password/change/', PortalPasswordChangeView.as_view(), name='portal_auth_password_change'),
    path('portal/password/reset/', PortalPasswordResetView.as_view(), name='portal_auth_password_reset'),
    path('portal/password/reset/confirm/<uidb64>[0-9A-Za-z]-<token>/', PortalPasswordResetConfirmView.as_view(), name='portal_password_reset_confirm'),
    path('portal/password/reset/done/', TemplateView.as_view(template_name='custom_password_reset_done.html'), name='portal_auth_password_reset_done'),
    path('portal/password/reset/complete/', TemplateView.as_view(template_name='custom_password_reset_complete.html'), name='portal_auth_password_reset_complete'),
    path('portal/password/change/done/', TemplateView.as_view(template_name='custom_password_change_complete.html'), name='portal_auth_password_change_done'),
]


registration_urlpatterns = [
    path('activate/complete/',
       TemplateView.as_view(template_name='activation_complete.html'),
       name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    path('activate_key/<activation_key>/',
       ActivationView.as_view(),
       name='registration_activate'),
    path('register/complete/',
       TemplateView.as_view(template_name='registration_complete.html'),
       name='registration_complete'),
    path('register/closed/',
       TemplateView.as_view(template_name='registration/registration_closed.html'),
       name='registration_disallowed'),
    ]
