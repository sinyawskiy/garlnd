import datetime
from django import forms
from django.conf import settings
import pytz
from apps.maps.forms import LockPasswordInput
from apps.tracks.models import Track


BootstrapUneditableInput = forms.TextInput
BootstrapDateTimeInput = forms.TextInput


class TrackForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Название трэка', 'class': 'span4'}), label='')
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'span4'}), label='Описание', required=False)
    lock_view = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'lock_checkbox'}), label='Закрыть трэк', required=False)
    view_password = forms.CharField(widget=LockPasswordInput(attrs={'placeholder': 'Пароль для просмотра карты', 'class': 'span4'}), label='', required=False)
    start_date = forms.DateTimeField(widget=BootstrapDateTimeInput(), label='Дата начала', required=False)
    end_date = forms.DateTimeField(widget=BootstrapDateTimeInput(), label='Дата окончания', required=False)

    class Meta:
        model = Track
        fields = ['title', 'description', 'device', 'lock_view','view_password', 'start_date', 'end_date']

    def __init__(self, *args, **kwargs):
        super(TrackForm, self).__init__(*args, **kwargs)

        local_tz = pytz.timezone(settings.TIME_ZONE)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59)

        if self.instance:
            start_date = self.instance.start_date.astimezone(local_tz) if self.instance.start_date else start_date
            end_date = self.instance.end_date.astimezone(local_tz) if self.instance.end_date else end_date
            if self.instance.view_password:
                self.initial['lock_view'] = True

        if self.initial:
            self.fields['start_date'].widget = BootstrapUneditableInput()
            self.fields['end_date'].widget = BootstrapUneditableInput()
            del self.fields['device']

        self.initial['start_date'] = start_date.strftime('%d.%m.%Y %H:%M')
        self.initial['end_date'] = end_date.strftime('%d.%m.%Y %H:%M')

    def clean_view_password(self):
        view_password = self.cleaned_data['view_password']
        lock_view = self.cleaned_data['lock_view']
        if lock_view and not len(view_password):
            raise forms.ValidationError('Если вы хотите закрыть трэк, то укажите пароль')
        elif not lock_view:
            return ''
        return view_password