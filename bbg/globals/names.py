# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 14:38:46 2014

@author: Brian Jacobowski
"""

import bbg.globals.constants as bc
from blpapi import Name

SVC_REF =  Name('//blp/refdata')
SVC_MKT =  Name('//blp/mktdata')
SVC_VWAP = Name('//blp/mktvwap')
SVC_BAR =  Name('//blp/mktbar')
SVC_FLDS = Name('//blp/apiflds')
SVC_PAGE = Name('//blp/pagedata')
SVC_TECH = Name('//blp/tasvc')
SVC_AUTH = Name('//blp/apiauth')

SESSION_START =   Name('SessionStarted')
SESSION_FAIL =    Name('SessionStartupFailure')
SESSION_TERM =    Name('SessionTerminated')
SESSION_CONDOWN = Name('SessionConnectionDown')

REQ_REF_HIST =   Name(bc.REQ_REF_HIST)
REQ_REF_DATA =   Name(bc.REQ_REF_DATA)
REQ_FLD_INFO =   Name('fieldInfoRequest')
REQ_FLD_SRCH =   Name('fieldSearchRequest')
REQ_FLD_CAT =    Name('categorizedFieldSearchRequest')
REQ_AUTH =       Name(bc.REQ_AUTH)
REQ_AUTH_LOGON = Name(bc.REQ_AUTH_LOGON)

RESP_REF_HIST =   Name('HistoricalDataResponse')
RESP_REF_DATA =   Name('ReferenceDataResponse')
RESP_FLD =        Name('fieldResponse')
RESP_FLD_CAT =    Name('categorizedFieldResponse')
RESP_AUTH =       Name('AuthorizationResponse')
RESP_LOGON =      Name('LogonStatusResponse')

ADJ_NORM =           Name('adjustmentNormal')
ADJ_ABNORM =         Name('adjustmentAbnormal')
ADJ_SPLIT =          Name('adjustmentSplit')
ADJ_FOLLOW =         Name('adjustmentFollowDPDF')
AUTH_SUCCESS =       Name('AuthorizationSuccess')
CAL_OVD =            Name('calendarCodeOverride')
CAL_OVDS =           Name('calendarOverrides')
CAL_OVDS_INFO =      Name('calendarOverridesInfo')
CAL_OVDS_OP =        Name('calendarOverridesOperation')
CAT_NM =             Name('categoryName')
CUR =                Name('currency')
DATA_TP =            Name('datatype')
DESC =               Name('description')
DOC =                Name('documentation')
EIDS =               Name('returnEids')
END_DT =             Name('endDate')
FLD_DATA =           Name('fieldData')
FLD_ID =             Name('fieldId')
FLD_INFO =           Name('fieldInfo')
FLD_OVD =            Name('FieldOverride')
FLDS =               Name('fields')
FTYPE =              Name('ftype')
ID =                 Name('id')
IP_ADDRESS =         Name('ipAddress')
MAX_DATA =           Name('maxDataPoints')
MNEMONIC =           Name('mnemonic')
NON_TRD_DY_OPT =     Name('nonTradingDayFillOption')
NON_TRD_DY_FILL =    Name('nonTradingDayFillMethod')
OVD =                Name('override')
OVD_OPT =            Name('overrideOption')
OVDS =               Name('overrides')
PER_ADJ =            Name('periodicityAdjustment')
PER_SEL =            Name('periodicitySelection')
PPTY =               Name('property')
PPTYS =              Name('properties')
PX_OPT =             Name('pricingOption')
REL_DT =             Name('relativeDate')
RTN_FMT =            Name('returnFormattedValue')
RTN_REL_DT =         Name('returnRelativeDate')
SEC =                Name('security')
SEC_DATA =           Name('securityData')
SECS =               Name('securities')
SEQ =                Name('sequenceNumber')
ST_DT =              Name('startDate')
UUID =               Name('uuid')
VAL =                Name('value')

ERR_FLD =            Name('fieldError')
ERR_FLDSRCH =        Name('fieldSearchError')
ERR_RESP =           Name('responseError')
ERR_SEC =            Name('securityError')
EXC_FLD =            Name('fieldException')
EXCS_FLD =           Name('fieldExceptions')
FAIL_AUTH =          Name('AuthorizationFailure')
REASON =             Name('reason')

INFO_ERR =           Name("errorInfo")
CAT =                Name('category')
CODE =               Name('code')
MSG =                Name('message')
SRC =                Name('source')
SUBCAT =             Name('subcategory')