# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 15:46:01 2014

@author: Brian
"""

import time
from functools import wraps
from contextlib import contextmanager

def memo(func):
    """decorator to memoize a function"""
    cache = {}
    @wraps(func)
    def wrap(*args, **kw):
        "session is removed as it isn't relevant to response"
        try:
            key = tuple(args)
            if len(kw) > 0:
                temp = kw.copy()
                temp.pop('session', None)
                key += tuple(temp.items())
            return cache[key]
        except TypeError:
            return func(*args, **kw)
        except KeyError:
            rtn = cache[key] = func(*args, **kw)
            return rtn
    return wrap


@contextmanager
def ignored(*exceptions):
    """decorator to ignore errors for a function"""
    try:
        yield
    except exceptions:
        pass


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        cr.next()
        return cr
    return start


class Timer(object):
    """decorator to time a function using 'with _Timer() as var:'"""
    def __init__(self):
        self.start = None
        self.end = None
        self.interval = None

    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, etype, value, traceback):
        self.end = time.clock()
        self.interval = self.end - self.start

    def __str__(self):
        minute, second = divmod(self.interval, 60)
#        hour, minute = divmod(minute, 60)
        return '{:02,.0f}:{:05.2f}'.format(minute, second)
