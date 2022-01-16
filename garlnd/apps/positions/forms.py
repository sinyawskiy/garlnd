import datetime
from django import forms
# from annoying.widgets import BootstrapDateTimeInput
from apps.devices.models import Device
from apps.positions.models import POSITIONS_EXPORT_FORMAT_CHOICES, GPX_FORMAT, Position

BootstrapDateTimeInput = forms.TextInput

class ExportPositionForm(forms.Form):
    start_date = forms.DateTimeField(widget=BootstrapDateTimeInput(), label='Дата начала', required=False)
    end_date = forms.DateTimeField(widget=BootstrapDateTimeInput(), label='Дата окончания', required=False)
    export_format = forms.ChoiceField(widget=forms.RadioSelect(attrs={'inline': True}), choices=POSITIONS_EXPORT_FORMAT_CHOICES, initial=GPX_FORMAT, label='Формат экспорта')

    def __init__(self, device_id=None, *args, **kwargs):
        super(ExportPositionForm, self).__init__(*args, **kwargs)
        if device_id is not None:
            try:
                device = Device.objects.get(id=device_id)
            except Device.DoesNotExist:
                pass
            else:
                self.initial['end_date'] = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
                if Position.objects.filter(device=device).count():
                    self.initial['start_date'] = Position.objects.filter(device=device).order_by('created_at').values_list('created_at', flat=True)[:1][0].strftime('%d.%m.%Y %H:%M')
                else:
                    self.initial['start_date'] = self.initial['end_date']
