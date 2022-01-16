from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import CustomUser


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label="Password",
        help_text="Raw passwords are not stored, so there is no way to see this user's password, but you can change the password using <a href=\"password/\">this form</a>.")

    class Meta:
        model = CustomUser
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def process_null_or_none_value(self, cleaned_data):
        if cleaned_data == 0:
            return 0
        elif isinstance(cleaned_data, str) and not len(cleaned_data):
            return None
        else:
            return cleaned_data

    def clean_max_maps_count(self):
        return self.process_null_or_none_value(self.cleaned_data['max_maps_count'])


    def clean_max_devices_count(self):
        return self.process_null_or_none_value(self.cleaned_data['max_devices_count'])

    def clean_max_rules_count(self):
        return self.process_null_or_none_value(self.cleaned_data['max_rules_count'])

    def clean_max_tracks_count(self):
        return self.process_null_or_none_value(self.cleaned_data['max_tracks_count'])
