#!/usr/bin/python
# -*- coding: utf-8 -*-
from captcha.fields import CaptchaField, CaptchaTextInput
from django import forms
from django.conf import settings
from django.core import validators
from django.forms import CharField, EmailInput


class EmailField(CharField):
    widget = EmailInput
    default_validators = [validators.EmailValidator('Введите правильный адрес электронной почты')]

    def clean(self, value):
        value = self.to_python(value).strip()
        return super(EmailField, self).clean(value)


class FeedbackForm(forms.Form):
    email = EmailField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Email для ответа', 'class': 'span4'}), required=True, label='')
    subject = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Тема сообщения', 'class': 'span4'}), required=False, label='')
    text = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class': 'span4'}), required=True, label='Сообщение')
    attachment = forms.FileField(label='Прикрепить файл', required=False)
    captcha = CaptchaField(widget=CaptchaTextInput(attrs={'placeholder': 'Введите код', 'class': 'span2'}), label='')

    def __init__(self, email=None, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        if email:
            self.initial['email'] = email

    def clean_attachment(self):
        if self.cleaned_data['attachment']:
            if self.cleaned_data['attachment'].size > settings.MAX_ATTACH_FEEDBACK_FILE_SIZE:
                raise forms.ValidationError('Превышен размер файла')
        return self.cleaned_data['attachment']
