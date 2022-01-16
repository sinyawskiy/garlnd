from django import forms
from apps.devices.models import Device


class DeviceAdminForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'owner', 'title', 'description', 'image',
            'add_position_password', 'width', 'color_rgb', 'connection_address',
        ]

    def clean_connection_address(self):
        return self.cleaned_data['connection_address'] or None


class DeviceForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Название устройства', 'class': 'span4'}), label='')
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'span4'}), label='Описание', required=False)
    color_rgb = forms.CharField(label='Цвет линии (RGB)') # widget=ColorFieldWidget(without_script=True, attrs={'readonly':'readonly'})
    add_position_password = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Идентификатор', 'class': 'span4'}), label='')
    width = forms.IntegerField(widget=forms.NumberInput(attrs={'step': '1'}), label='Ширина линии, px', min_value=1, max_value=15)
    image = forms.ImageField(label='Изображение', required=False) #widget=BootstrapImageWidget(),

    class Meta:
        model = Device
        fields = ['title', 'add_position_password', 'description', 'color_rgb', 'width', 'image',]

    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.initial['width'] = self.instance.width if self.instance.width else 7
            self.initial['color_rgb'] = self.instance.get_color()

    def clean_image(self):
        if self.cleaned_data['image']:
            if self.cleaned_data['image'].size>1024*1024:
                raise forms.ValidationError("Файл не более 1 Мб")
        return self.cleaned_data['image']
