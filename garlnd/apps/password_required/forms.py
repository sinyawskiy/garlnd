from django import forms
from apps.maps.models import Map
from apps.tracks.models import Track


class MapAuthenticationForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль', 'class': 'span4'}), label='Пароль')

    def __init__(self, map_id=None, request=None, *args, **kwargs):
        self.map_id = map_id
        self.request = request
        super(MapAuthenticationForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')

        try:
            event_map = Map.objects.get(id=self.map_id)
        except Map.DoesNotExist:
            raise forms.ValidationError('Карта не найдена')
        else:
            correct_password = event_map.view_password

        if not correct_password:
            raise forms.ValidationError('Пароль не задан')

        if not (password == correct_password or
                password.strip() == correct_password):
            raise forms.ValidationError('Пароль введен неверно')

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError('Ваш браузер не поддерживает Cookies')

        return self.cleaned_data


class TrackAuthenticationForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль', 'class': 'span4'}), label='Пароль')

    def __init__(self, track_id=None, request=None, *args, **kwargs):
        self.track_id = track_id
        self.request = request
        super(TrackAuthenticationForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')

        try:
            event_map = Track.objects.get(id=self.track_id)
        except Track.DoesNotExist:
            raise forms.ValidationError('Карта не найдена')
        else:
            correct_password = event_map.view_password

        if not correct_password:
            raise forms.ValidationError('Пароль не задан')

        if not (password == correct_password or
                password.strip() == correct_password):
            raise forms.ValidationError('Пароль введен неверно')

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError('Ваш браузер не поддерживает Cookies')

        return self.cleaned_data