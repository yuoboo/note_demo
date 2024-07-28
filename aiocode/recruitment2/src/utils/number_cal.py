# coding: utf-8
from decimal import Decimal


def to_decimal(num, places=3):
    if num == 1.0:
        return 1
    buf = '0.{}'.format('0' * places)
    return Decimal(num).quantize(Decimal(buf))
