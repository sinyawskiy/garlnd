# from bootstrap_toolkit.widgets import BootstrapUneditableInput
from django import forms
from django.conf import settings
from apps.devices.models import Device
from apps.maps.models import Map

BootstrapUneditableInput = forms.TextInput


class LockPasswordInput(forms.TextInput):
    bootstrap = {
        'append': 'Создать пароль',
        'append_element_classes': ('btn', 'create_password')
    }


class MapForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Название карты', 'class': 'span4'}), label='')
    lock_view = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'lock_checkbox'}), label='Закрыть карту', required=False)
    view_password = forms.CharField(widget=LockPasswordInput(attrs={'placeholder': 'Пароль для просмотра карты', 'class': 'span4'}), label='', required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'span4'}), label='Описание', required=False)
    longitude = forms.FloatField(widget=BootstrapUneditableInput(), label='Долгота', required=False)
    latitude = forms.FloatField(widget=BootstrapUneditableInput(), label='Широта', required=False)
    zoom = forms.IntegerField(widget=BootstrapUneditableInput(), label='Масштаб', required=False)

    class Meta:
        model = Map
        fields = ['title', 'lock_view', 'view_password', 'description']

    def __init__(self, *args, **kwargs):
        super(MapForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.initial['longitude'] = self.instance.longitude if self.instance.longitude else settings.DEFAULT_MAP_LONGITUDE
            self.initial['latitude'] = self.instance.latitude if self.instance.latitude else settings.DEFAULT_MAP_LATITUDE
            self.initial['zoom'] = self.instance.zoom if self.instance.zoom else settings.DEFAULT_MAP_ZOOM
            if self.instance.view_password:
                self.initial['lock_view'] = True
        elif not self.instance:
            self.initial['longitude'] = settings.DEFAULT_MAP_LONGITUDE
            self.initial['latitude'] = settings.DEFAULT_MAP_LATITUDE
            self.initial['zoom'] = settings.DEFAULT_MAP_ZOOM

    def clean_view_password(self):
        view_password = self.cleaned_data['view_password']
        lock_view = self.cleaned_data['lock_view']
        if lock_view and not len(view_password):
            raise forms.ValidationError('Если вы хотите закрыть карту, то укажите пароль')
        elif not lock_view:
            return ''
        return view_password

    def clean_add_event_password(self):
        add_event_password = self.cleaned_data['add_event_password']
        use_monitoring = self.cleaned_data['use_monitoring']
        if use_monitoring and not len(add_event_password):
            raise forms.ValidationError('Для регистрации событий, системы мониторинга должны быть авторизованы с паролем')
        elif not use_monitoring:
            return ''
        return add_event_password


class AddDeviceToMapForm(forms.Form):
    device = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'span4'}), queryset=None, empty_label=None, required=False, label='Устройство')

    def __init__(self, map_to_adding, *args, **kwargs):
        super(AddDeviceToMapForm, self).__init__(*args, **kwargs)
        added_devices = map_to_adding.devices.all()
        self.fields['device'].queryset = Device.objects.filter(owner=map_to_adding.owner).exclude(id__in=added_devices)
