import re
from django.core.validators import RegexValidator


# sms_phone_validator = RegexValidator('^8{1}[0-9]{10}|\w{0}$', message='81234567890')
sms_phone_validator = RegexValidator('^\([0-9]{3}\) [0-9]{3}-[0-9]{2}-[0-9]{2}$', message='(812) 123-45-67')


class PhoneNumber(object):

    @staticmethod
    def phone_number_sms_format(number):
        if isinstance(number, str):
            number = number.decode('utf8')
        if len(number):
            number = '7%s' % number[1:]
        return number

    @staticmethod
    def phone_number_beauty_format(number):
        if isinstance(number, str):
            number = number.decode('utf8')
        if len(number):
            number = '(%s) %s-%s-%s' % (number[1:4], number[4:7], number[7:9], number[9:])
        return number

    @staticmethod
    def phone_number_base_format(number):
        if isinstance(number, str):
            number = number.decode('utf8')

        RUSSIA_PREFIXES = ['812', '901', '902', '903', '904', '905', '906', '908', '909',
                           '910', '911', '912', '913', '914', '915', '916', '917', '918',
                           '919', '920', '921', '922', '923', '924', '925', '926', '927',
                           '928', '929', '930', '931', '932', '933', '934', '936', '937',
                           '938', '950', '951', '952', '953', '960', '961', '962', '963',
                           '964', '965', '980', '981', '982', '983', '984', '985', '987',
                           '988', '989', '997']

        def padd_to(padd_str, padd_len):
            while len(padd_str) < padd_len:
                padd_str = '%s%s' % ('0', padd_str)
            return padd_str

        number_arr = re.split('[\+\- \(\)]+',number)
        number = ''.join(number_arr)
        len_number = len(number)
        if len_number in range(7, 10):
            if len_number > 7:
                number = number[len_number-7:]
            number = '8812%s' % number
        elif len_number > 9:
            number = number[len_number-10:]
            prefix = number[:3]
            if not prefix in RUSSIA_PREFIXES:
                prefix = '812'
            number = '8%s%s' % (prefix,number[3:])
        return number