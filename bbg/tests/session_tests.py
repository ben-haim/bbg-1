# -*- coding: utf-8 -*-
"""
Created on Wed Jul 02 10:48:48 2014

@author: Brian Jacobowski <bjacobowski.dev@gmail.com>
"""

from nose.tools import *
from bbg.bloomberg.session import Session
import bbg.globals.constants as bc
import bbg.globals.names as bn

def test_session():
    with Session() as session:
        assert_true(session.started)

def test_service():
    with Session() as session:
        auth = session.getService(bc.SVC_AUTH)
        bar = session.getService(bc.SVC_BAR)
        flds = session.getService(bc.SVC_FLDS)
        mkt = session.getService(bc.SVC_MKT)
        pg = session.getService(bc.SVC_PAGE)
        ref = session.getService(bc.SVC_REF)
        tech = session.getService(bc.SVC_TECH)
        vwap = session.getService(bc.SVC_VWAP)

        assert_equal(auth.name(), bn.SVC_AUTH)
        assert_equal(bar.name(), bn.SVC_BAR)
        assert_equal(flds.name(), bn.SVC_FLDS)
        assert_equal(mkt.name(), bn.SVC_MKT)
        assert_equal(pg.name(), bn.SVC_PAGE)
        assert_equal(ref.name(), bn.SVC_REF)
        assert_equal(tech.name(), bn.SVC_TECH)
        assert_equal(vwap.name(), bn.SVC_VWAP)
