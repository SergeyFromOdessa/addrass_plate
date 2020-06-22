import re

# house_number_validator = re.compile(r'(?P<number1>^[1-9]\d*(-[1-9]\d*)?)'
#                                     r'((?P<letter2>[А-Я]+)'
#                                     r'|((?P<slash>/)(?P<number2>[1-9]\d*)(?P<letter3>[А-Я]*))'
#                                     r'|((?P<sk> к)(?P<corp>[1-9]\d*)))?$')

house_number_re_tuple = (
    re.compile(r'^(?P<lvl1>[1-9]\d*(-[1-9]\d*)?)$'),
    re.compile(r'^(?P<lvl1>[1-9]\d*(-[1-9]\d*)?)(?P<lvl2c>[А-Я]+)$'),
    re.compile(r'^(?P<lvl1>[1-9]\d*(-[1-9]\d*)?)(?P<lvl2_slash>/)(?P<lvl2s>[1-9]\d*)(?P<lvl3>[А-Я]*)$'),
    re.compile(r'^(?P<lvl1>[1-9]\d*(-[1-9]\d*)?)(?P<lvl2c> к[1-9]\d*)$'),
)

# house_number_arrow_validator = re.compile(r'(?P<lvl_a1>^[1-9]\d*(-[1-9]\d*)?)(?P<lvl_a2c>[А-Я]+)?$')

house_number_arrow_re_tuple = (
    re.compile(r'(?P<lvl_a1>^[1-9]\d*(-[1-9]\d*)?)(?P<lvl_a2c>[А-Я]+)?$'),
)
