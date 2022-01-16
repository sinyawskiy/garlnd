#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import string


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
     return ''.join(random.choice(chars) for x in range(size))

def padd_to(input_str, pad_len, filler='0'):
    str_len = len(input_str)
    if str_len < pad_len:
        input_str = '%s%s' % (filler*(pad_len-str_len), input_str)
    return input_str