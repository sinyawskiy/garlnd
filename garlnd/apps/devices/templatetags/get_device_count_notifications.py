#!/usr/bin/python
# -*- coding: utf-8 -*-
from django import template
register = template.Library()

@register.simple_tag
def get_device_count_notifications(device, rule_type):
    return device.get_count_notifications(rule_type)