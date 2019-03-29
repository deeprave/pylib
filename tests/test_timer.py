# -*- coding: utf-8 -*-
import time
from datetime import timedelta

from pylib.timer import timer


def sleepy(seconds):
    # type: (float) -> float
    time.sleep(seconds)
    return seconds

def test_timer():
    TESTVALUE = 2.0
    value, duration = timer(sleepy, TESTVALUE)
    assert value == TESTVALUE
    lower = timedelta(seconds=TESTVALUE, milliseconds=-100)
    upper = timedelta(seconds=TESTVALUE, milliseconds=100)
    assert upper > duration > lower
