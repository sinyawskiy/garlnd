from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView
# from apps.custom_registration.urls import registration_urlpatterns
from apps.password_required.views import map_login, track_login
from django.views.static import serve

admin.site.site_header = settings.ADMIN_SITE_HEADER

admin.autodiscover()

urlpatterns = [
    path('', include('apps.account.urls')),
    path('maps/', include('apps.maps.urls')),
    path('devices/', include('apps.devices.urls')),
    path('positions/', include('apps.positions.urls')),
    path('tracks/', include('apps.tracks.urls')),
    path('rules/', include('apps.rules.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('registration/', include('apps.custom_registration.urls')),
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('map_password_required/<map_id>/', map_login),
    path('track_password_required/<track_id>/', track_login)
]

# urlpatterns += registration_urlpatterns

urlpatterns.extend(staticfiles_urlpatterns())

urlpatterns.extend([
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^tiles/(?P<proxy_kwargs>.*)$', RedirectView.as_view(url='https://tile.openstreetmap.org/%(proxy_kwargs)s')),
])
