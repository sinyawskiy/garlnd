from django.contrib import admin
from registration.admin import RegistrationAdmin
from registration.models import RegistrationProfile
from .models import CustomRegistrationProfile

admin.site.unregister(RegistrationProfile)
admin.site.register(CustomRegistrationProfile, RegistrationAdmin)
