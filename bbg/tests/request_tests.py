# -*- coding: utf-8 -*-
"""
Created on Wed Jul 02 11:47:12 2014

@author: Brian Jacobowski <bjacobowski.dev@gmail.com>
"""

from nose.tools import *
from bbg import (request_refdata, request_mult_refdata,
                 request_refhist, Timer)
import datetime as dt
import pandas as pd
import numpy as np

END_DT = dt.date.today()
ST_DT = dt.date(END_DT.year, END_DT.month - 1, END_DT.day)

EQY = ['ry us equity', 'jpm us equity']
EQY_F = ['cur_mkt_cap', 'px_last']

MTGE = ['31392DR20 Mtge', '31394CCV2 Mtge']
MTGE_F = ['PX_BID', 'SETTLE_DT', 'PX_BID', 'MTG_CASH_FLOW']
MTGE_O = [('MTG_PREPAY_TYP', 'CPR'), ('PREPAY_SPEED_VECTOR', '18 24 R 10')]

def test_eqy():
    rtn1 = request_refdata(EQY, EQY_F)
    rtn2 = request_refdata(tuple(EQY), EQY_F)
    rtn3 = request_refdata(EQY[0], EQY_F)

    eqy = [x.upper() for x in EQY]
    [assert_in(x, rtn1) for x in eqy]
    assert_equal(rtn1, rtn2)
    assert_equal(rtn1[eqy[0]], rtn3[eqy[0]])

def test_mtge():
    rtn1 = request_refdata(MTGE, MTGE_F, MTGE_O)
    rtn2 = request_refdata(tuple(MTGE), MTGE_F, MTGE_O)
    rtn3 = request_refdata(MTGE[0], MTGE_F, MTGE_O)

    mtge = [x.upper() for x in MTGE]
    [assert_in(x, rtn1) for x in mtge]
    [assert_is_not_none(x) for x in (rtn1, rtn2, rtn3)]

def test_mult():
    bond = '88059FAN1 CORP'
    px = request_refdata(bond, 'PX_BID')
    arr = np.arange(0.8, 1.21, 0.1) * px[bond]['PX_BID']
    reqs = {i: (bond, 'YLD_CNV_BID', ('PX_BID', x))
            for i, x in enumerate(arr)}
    with Timer() as tic:
        rtn = request_mult_refdata(reqs)
    assert_greater(tic, 0)
    out = np.array([rtn[i][bond]['YLD_CNV_BID'] for i in range(len(rtn))])
    assert_equal(len(arr), len(out))

def test_hist():
    eqy = EQY[0].upper()
    rtn = request_refhist(EQY[0], EQY_F[0], None, ST_DT, END_DT)
    assert_is_not_none(rtn)
    assert_true(isinstance(rtn[eqy], pd.core.frame.DataFrame))

def test_invalidflds():
    fld = 'nonsense'
    reqs = {1:(EQY, fld), 2:(EQY, fld)}

    rtn1 = request_refdata(EQY, fld)
    rtn2 = request_mult_refdata(reqs)
    rtn3 = request_refhist(EQY, fld)

    [assert_is_not_none(x) for x in (rtn1, rtn2, rtn3)]
