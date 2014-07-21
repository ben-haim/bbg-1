# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 11:43:33 2014

@author: Brian
"""

import datetime as dt
from dateutil.parser import parse

_FORMAT_DTTM_TO_BBG = ur'%Y-%m-%dT%H:%M:%S'
_FORMAT_DTTM_FROM_BBG = '%m/%d/%Y %H:%M:%S'
_FORMAT_DT_TO_BBG = '%Y%m%d'
_FORMAT_DT_FROM_BBG = '%m/%d/%Y'
_FORMAT_DT_LG = '%m-%d-%Y'
_FORMAT_DT_ST = '%m-%d-%y'
_FORMAT_TM_TO_BBG = '%H:%M'
_FORMAT_TM_FROM_BBG = '%H:%M:%S.%f'
_FORMAT_TM = '%H:%M:%S'


class _dateSuper:
    """Super-class creating bloomber specific date functions"""
    _DT_FORMATS = []

    @classmethod
    def from_string(cls, string):
        _new = parse(string)
        if _new is not None:
            rtn = cls(dt_obj=_new)
        else:
            rtn = None
        return rtn


    @classmethod
    def from_unknown_type(cls, var):
        try:
            if isinstance(var, cls):
                rtn = var
            elif isinstance(var, str):
                rtn = cls.from_string(var)
            elif isinstance(var, (dt.datetime, dt.date, dt.time)):
                rtn = cls(dt_obj=var)
            else:
                raise TypeError('Expected datetime obj or string, got {0}'
                                .format(type(var)))
        except TypeError as err:
            print err
            return None
        return rtn


    def str_to_bbg(self):
        return self.strftime(self._DT_FORMATS[0])


class BbgDateTime(dt.datetime, _dateSuper):
    """
    sub-class of datetime.date that provides methods for sending/receiving
    bloomberg dates.
    """
    _DT_FORMATS = [_FORMAT_DTTM_TO_BBG, _FORMAT_DTTM_FROM_BBG, _FORMAT_DT_LG,
                   _FORMAT_DT_ST]

    def __new__(cls, year=None, month=None, day=None, hour=None,
                 minute=None, second=None, microsecond=None,
                 tzinfo=None, dt_obj=None):
        if dt_obj is not None and isinstance(dt_obj, (dt.date, dt.datetime)):
            year = dt_obj.year
            month = dt_obj.month
            day = dt_obj.day
            if isinstance(dt_obj, dt.datetime):
                hour = dt_obj.hour
                minute = dt_obj.minute
                second = dt_obj.second
                microsecond = dt_obj.microsecond
                tzinfo = dt_obj.tzinfo
        lst = [year, month, day, hour, minute, second, microsecond, tzinfo]
        args = [x for x in lst if x is not None]
        return dt.datetime.__new__(cls, *args)


class BbgDate(dt.date, _dateSuper):
    """
    sub-class of datetime.date that provides methods for sending/receiving
    bloomberg dates.
    """
    _DT_FORMATS = [_FORMAT_DT_TO_BBG, _FORMAT_DT_FROM_BBG, _FORMAT_DT_LG,
                   _FORMAT_DT_ST]

    def __new__(self, year=None, month=None, day=None, dt_obj=None):
        if dt_obj is not None and isinstance(dt_obj, (dt.date, dt.datetime)):
            year = dt_obj.year
            month = dt_obj.month
            day = dt_obj.day
        return dt.date.__new__(self, year, month, day)


class BbgTime(dt.time, _dateSuper):
    """
    sub-class of datetime.time that provides methods for sending/receiving
    bloomberg times.
    """
    _DT_FORMATS = [_FORMAT_TM_TO_BBG, _FORMAT_TM_FROM_BBG, _FORMAT_TM]

    def __new__(self, hour=None, minute=None, second=None, microsecond=None,
                 tzinfo=None, dt_obj=None):
        if dt_obj is not None and isinstance(dt_obj, (dt.time, dt.datetime)):
            hour = dt_obj.hour
            minute = dt_obj.minute
            second = dt_obj.second
            microsecond = dt_obj.microsecond
            tzinfo = dt_obj.tzinfo
        return dt.time.__new__(self, hour, minute, second, microsecond,
                                             tzinfo)


def main():
    """main function..."""

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Ctrl+C pressed. Stopping..."
