# -*- coding: utf-8 -*-
"""
Created on Wed Jul 02 11:33:42 2014

@author: Brian Jacobowski <bjacobowski.dev@gmail.com>
"""

from nose.tools import *
import bbg.utils.date as bdt
from bbg.utils.date import BbgDate, BbgDateTime, BbgTime
import datetime as dt

date_tup = (2014, 6, 15)
time_tup = (13, 30, 5, 1)
datetime_tup = date_tup + time_tup

date1 = dt.date(*date_tup)
time1 = dt.time(*time_tup)
datetime1 = dt.datetime(*datetime_tup)

dttm_fmt1 = bdt._FORMAT_DTTM_TO_BBG
dttm_fmt1_s = '2014-06-15T13:30:05'
dttm_fmt2 = bdt._FORMAT_DTTM_FROM_BBG
dttm_fmt2_s = '06/15/2014 13:30:05'

dt_fmt1 = bdt._FORMAT_DT_TO_BBG
dt_fmt1_s = '20140615'
dt_fmt2 = bdt._FORMAT_DT_FROM_BBG
dt_fmt2_s = '06/15/2014'
dt_fmt3 = bdt._FORMAT_DT_LG
dt_fmt3_s = '06-15-2014'
dt_fmt4 = bdt._FORMAT_DT_ST
dt_fmt4_s = '06-15-14'

tm_fmt1 = bdt._FORMAT_TM_TO_BBG
tm_fmt1_s = '13:30'
tm_fmt2 = bdt._FORMAT_TM_FROM_BBG
tm_fmt2_s = '13:30:05.000001'
tm_fmt3 = bdt._FORMAT_TM
tm_fmt3_s = '13:30:05'

def test_datetime():
    b_dttm = []
    b_dttm.append(BbgDateTime(*datetime_tup))
    b_dttm.append(BbgDateTime(dt_obj=datetime1))
    b_dttm.append(BbgDateTime.from_string(dttm_fmt1_s))
    b_dttm.append(BbgDateTime.from_string(dttm_fmt2_s))
    b_dttm.append(BbgDateTime.from_unknown_type(b_dttm[0]))
    b_dttm.append(BbgDateTime.from_unknown_type(datetime1))
    b_dttm.append(BbgDateTime.from_unknown_type(dttm_fmt1_s))
    b_dttm.append(BbgDateTime.from_unknown_type(dttm_fmt2_s))

#    print '\nBbgDateTimes test: ', all([x.strftime(dttm_fmt2) ==
#        datetime1.strftime(dttm_fmt2) for x in b_dttm])

    assert_true(all([x.strftime(dttm_fmt2) ==
        datetime1.strftime(dttm_fmt2) for x in b_dttm]))


def test_date():
    b_dt = []
    b_dt.append(BbgDate(*date_tup))
    b_dt.append(BbgDate(dt_obj=date1))
    b_dt.append(BbgDate.from_string(dt_fmt1_s))
    b_dt.append(BbgDate.from_string(dt_fmt2_s))
    b_dt.append(BbgDate.from_unknown_type(b_dt[0]))
    b_dt.append(BbgDate.from_unknown_type(date1))
    b_dt.append(BbgDate.from_unknown_type(dt_fmt1_s))
    b_dt.append(BbgDate.from_unknown_type(dt_fmt2_s))

#    print 'BbgDates test: ', all([x == datetime1 for x in b_dt])

    assert_true(all([x == datetime1 for x in b_dt]))

def test_time():
    b_tm = []
    b_tm.append(BbgTime(*time_tup))
    b_tm.append(BbgTime(dt_obj=time1))
    b_tm.append(BbgTime.from_string(tm_fmt2_s))
    b_tm.append(BbgTime.from_string(tm_fmt3_s))
    b_tm.append(BbgTime.from_unknown_type(b_tm[0]))
    b_tm.append(BbgTime.from_unknown_type(time1))
    b_tm.append(BbgTime.from_unknown_type(tm_fmt2_s))
    b_tm.append(BbgTime.from_unknown_type(tm_fmt3_s))

#    print 'BbgTimes test: ', all([x.strftime(tm_fmt3) ==
#        datetime1.strftime(tm_fmt3) for x in b_tm])

    assert_true(all([x.strftime(tm_fmt3) ==
        datetime1.strftime(tm_fmt3) for x in b_tm]))
