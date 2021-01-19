import re

from django.core.exceptions import ValidationError


def validate_email(value):
    regex = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

    if not regex.match(value):
        return False
    return True


def validate_password(value):
    regex = re.compile('^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$')

    if not regex.match(value):
        return False
    return True


def validate_phone_number(value):
    regex     = re.compile('010-?[0-9]{4}-?[0-9]{4}')
    length_pn = 11

    if not regex.match(value):
        return False

    if len(value) > length_pn:
        return False

    return True
