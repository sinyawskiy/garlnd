from django import forms
from apps.devices.models import Device
from .models import Rule

BootstrapUneditableInput = forms.TextInput


class RuleAdminForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = ['owner','title','description','email','phone_number_sms','device','rule_type','max_speed',
                  'initial_longitude','initial_latitude', 'distance_offset', 'auto_reactivate', 'is_active',
                  'activated_at','deactivated_at']

    def clean_email(self):
        return self.cleaned_data['email'] or None

    def clean_phone_number_sms(self):
        return self.cleaned_data['phone_number_sms'] or None

    def clean_max_speed(self):
        return self.cleaned_data['max_speed'] or None

    def clean_initial_longitude(self):
        return self.cleaned_data['initial_longitude'] or None

    def clean_initial_latitude(self):
        return self.cleaned_data['initial_latitude'] or None

    def clean_distance_offset(self):
        return self.cleaned_data['distance_offset'] or None


class RuleForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Название правила', 'class': 'span4'}), label='')
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'span4'}), label='Описание', required=False)
    device = forms.ModelChoiceField(label='Трэкер', queryset=None, help_text='Активация правила происходит после переподключения устройства')
    max_speed = forms.CharField(widget=forms.NumberInput(attrs={'min':1, 'step':'0.1', 'data-type':'rule', 'data-rule_id': '[4]'}), label='Порог скорости (км/ч)', required=False)
    initial_longitude = forms.FloatField(widget=BootstrapUneditableInput(attrs={'data-type':'rule', 'data-rule_id': '[1,2]'}), label='Долгота (градусы)', required=False)
    initial_latitude = forms.FloatField(widget=BootstrapUneditableInput(attrs={'data-type':'rule', 'data-rule_id': '[1,2]'}), label='Широта (градусы)', required=False)
    distance_offset = forms.CharField(widget=forms.NumberInput(attrs={'min': '0.025', 'max':'25', 'step':'0.025', 'data-type':'rule', 'data-rule_id': '[1,2]'}), label='Радиус зоны (км)', required=False)

    def __init__(self, request, *args, **kwargs):
        super(RuleForm, self).__init__(*args, **kwargs)
        self.initial['email'] = self.instance.email if self.instance.email else request.user.email
        self.initial['max_speed'] = self.instance.max_speed if self.instance.max_speed else ''
        self.fields['device'].queryset = Device.objects.filter(owner=request.user)
        self.initial['phone_number_sms'] = Rule.phone_number_beauty_format(self.instance.phone_number_sms) if self.instance.phone_number_sms else ''


    class Meta:
        model = Rule
        fields = ['title', 'description', 'email', 'phone_number_sms', 'device', 'rule_type',
                  'max_speed', 'initial_longitude', 'initial_latitude', 'distance_offset',
                  'auto_reactivate', 'is_active']

    def clean_email(self):
        return self.cleaned_data['email'] or None

    def clean_phone_number_sms(self):
        return self.cleaned_data['phone_number_sms'] or None

    def clean_max_speed(self):
        return self.cleaned_data['max_speed'] or None

    def clean_initial_longitude(self):
        return self.cleaned_data['initial_longitude'] or None

    def clean_initial_latitude(self):
        return self.cleaned_data['initial_latitude'] or None

    def clean_distance_offset(self):
        return self.cleaned_data['distance_offset'] or None