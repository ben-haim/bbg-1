# -*- coding: utf-8 -*-
"""
Created on Wed Jul 02 11:47:12 2014

@author: Brian Jacobowski <bjacobowski.dev@gmail.com>
"""

from nose.tools import *
from bbg import (get_data_bbg, get_multidata_bbg,
                 get_histdata_bbg, get_sensitivity_bbg, get_fldinfo_bbg)
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
    rtn1 = get_data_bbg(EQY, EQY_F)
    rtn2 = get_data_bbg(tuple(EQY), EQY_F)
    rtn3 = get_data_bbg(EQY[0], EQY_F)

    eqy = [x.upper() for x in EQY]
    [assert_in(x, rtn1) for x in eqy]
    assert_equal(rtn1, rtn2)
    assert_equal(rtn1[eqy[0]], rtn3[eqy[0]])

def test_mtge():
    rtn1 = get_data_bbg(MTGE, MTGE_F, MTGE_O)
    rtn2 = get_data_bbg(tuple(MTGE), MTGE_F, MTGE_O)
    rtn3 = get_data_bbg(MTGE[0], MTGE_F, MTGE_O)

    mtge = [x.upper() for x in MTGE]
    [assert_in(x, rtn1) for x in mtge]
    [assert_is_not_none(x) for x in (rtn1, rtn2, rtn3)]

def test_mult():
    bond = '88059FAN1 CORP'
    px = get_data_bbg(bond, 'PX_BID')
    arr = np.arange(0.8, 1.21, 0.1) * px[bond]['PX_BID']
    reqs = {i: (bond, 'YLD_CNV_BID', ('PX_BID', x))
            for i, x in enumerate(arr)}
    rtn = get_multidata_bbg(reqs)
    out = np.array([rtn[i][bond]['YLD_CNV_BID'] for i in range(len(rtn))])
    assert_equal(len(arr), len(out))

def test_hist():
    eqy = EQY[0].upper()
    rtn = get_histdata_bbg(EQY[0], EQY_F[0], None, ST_DT, END_DT)
    assert_is_not_none(rtn)
    assert_true(isinstance(rtn[eqy], pd.core.frame.DataFrame))

def test_invalidflds():
    fld = 'nonsense'
    reqs = {1:(EQY, fld), 2:(EQY, fld)}

    rtn1 = get_data_bbg(EQY, fld)
    rtn2 = get_multidata_bbg(reqs)
    rtn3 = get_histdata_bbg(EQY, fld)

    [assert_is_not_none(x) for x in (rtn1, rtn2, rtn3)]
