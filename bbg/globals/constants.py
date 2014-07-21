# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 15:28:47 2014

@author: Brian
"""

from blpapi.datatype import DataType as bdt

#Bloomberg sectors (yellow keys)
BBG_PRODUCT_TYPES = ['GOVT', 'CORP', 'MTGE', 'M-MKT', 'MUNI', 'PFD',
                     'EQUITY', 'CMDTY', 'INDEX', 'CURNCY']

#blpapi services
SVC_REF =  '//blp/refdata'
SVC_MKT =  '//blp/mktdata'
SVC_VWAP = '//blp/mktvwap'
SVC_BAR =  '//blp/mktbar'
SVC_FLDS = '//blp/apiflds'
SVC_PAGE = '//blp/pagedata'
SVC_TECH = '//blp/tasvc'
SVC_AUTH = '//blp/apiauth'

#blpapi request names (in str format, bb.Name format in bbg.globals.names)
REQ_REF_HIST =   'HistoricalDataRequest'
REQ_REF_DATA =   'ReferenceDataRequest'
REQ_FLD_INFO =   'FieldInfoRequest'
REQ_FLD_SRCH =   'FieldSearchRequest'
REQ_FLD_CAT =    'CategorizedFieldSearchRequest'
REQ_AUTH =       'AuthorizationRequest'
REQ_AUTH_LOGON = 'LogonStatusRequest'

#blpapi Element names
EL_REF_SEC_DATA = 'ReferenceSecurityData'
EL_REF_FLD_DATA = 'ReferenceFieldData'
EL_REF_HIST_TBL = 'HistoricalDataTable'
EL_REF_HIST_ROW = 'HistoricalDataRow'

#blpapi constants
FLD_OVDBL = 'fieldoverridable'
FLDS = 'fields'
IDS =  'identifiers'
OVDBL = 'overridable'
OVDS = 'overrides'

ELEMENT_DATATYPE_NAMES = {
    bdt.BOOL:           "BOOL",
    bdt.CHAR:           "CHAR",
    bdt.BYTE:           "BYTE",
    bdt.INT32:          "INT32",
    bdt.INT64:          "INT64",
    bdt.FLOAT32:        "FLOAT32",
    bdt.FLOAT64:        "FLOAT64",
    bdt.STRING:         "STRING",
    bdt.BYTEARRAY:      "BYTEARRAY",
    bdt.DATE:           "DATE",
    bdt.TIME:           "TIME",
    bdt.DECIMAL:        "DECIMAL",
    bdt.DATETIME:       "DATETIME",
    bdt.ENUMERATION:    "ENUMERATION",
    bdt.SEQUENCE:       "SEQUENCE",
    bdt.CHOICE:         "CHOICE",
    bdt.CORRELATION_ID: "CORRELATION_ID"
}
