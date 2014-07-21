# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 10:25:10 2014

@author: Brian
"""

import bbg.globals.constants as bc
import bbg.globals.exceptions as be
import bbg.globals.names as bn
from bbg.utils.misc import format_fld_name

import pandas as pd
from blpapi.event import Event
from collections import defaultdict, namedtuple


def processEvent(event, session):
    """Acts as event handler for asynchronous bloomberg requests"""
    event_type = event.eventType()
    FUNC_EVENT[event_type](event, session)
#    _proc_print_basic(event, session)


def _proc_event_admin(event, session):
    """process bb admin event"""
    pass


def _proc_event_status(event, session):
    """process bb status event"""
    try:
        for msg in event:
            msg_type = msg.messageType()
            if msg_type == bn.SESSION_START:
                __ = session.queue.get()
                #print 'Session started...'
                session.started = True
                session.queue.task_done()
            elif msg_type == bn.SESSION_FAIL:
                session.started = False
                raise be.SessionError('Session failed to open')
            elif msg_type == bn.SESSION_CONDOWN:
                while session.queue.qsize() > 0:
                    __ = session.queue.get()
                try:
                    while True:
                        session.queue.task_done()
                except ValueError:
                    pass
    except be.SessionError as err:
        print err


def _proc_event_resp(event, session):
    """process bb response/partial response event"""
    return_dict = session.correlation_ids
    event_type = event.eventType()
    for msg in event:
        try:
            #Do not allow multiple correlationIds in a message,
            #it's overly complicated
            corr_id = msg.correlationIds()[0].value()
            msg_type = msg.messageType()
            FUNC_RESPONSE[msg_type](msg, return_dict[corr_id])
        except be.ResponseError as err:
            print err
    if event_type == Event.RESPONSE:
        session.queue.task_done()


def _proc_event_sub_data(event, session):
    """process bb subscription event"""
    pass


def _proc_event_timeout(event, session):
    """process bb timeout event"""
    pass


def _proc_event_pass(event, __=None):
    """process to pass on bb event"""
    pass


def _proc_print_basic(event, session):
    """debugging process to print out an event"""
    try:
        for msg in event:
#            print event.eventType()
            print msg.correlationIds()[0].value()
            print msg
#        try:
#            if event.eventType() == Event.SESSION_STATUS:
#                __ = session.queue.get()
#            session.queue.task_done()
#        except ValueError:
#            pass
    except Exception as err:
        print err


FUNC_EVENT = {
    Event.ADMIN: _proc_event_admin,
    Event.SESSION_STATUS: _proc_event_status,
    Event.SUBSCRIPTION_STATUS: _proc_event_status,
    Event.REQUEST_STATUS: _proc_event_status,
    Event.RESPONSE: _proc_event_resp,
    Event.PARTIAL_RESPONSE: _proc_event_resp,
    Event.SUBSCRIPTION_DATA: _proc_event_sub_data,
    Event.SERVICE_STATUS: _proc_event_status,
    Event.TIMEOUT: _proc_event_timeout,
    Event.AUTHORIZATION_STATUS: _proc_event_status,
    Event.RESOLUTION_STATUS: _proc_event_status,
    Event.TOPIC_STATUS: _proc_event_status,
    Event.TOKEN_STATUS: _proc_event_status,
    Event.REQUEST: _proc_event_pass,
    Event.UNKNOWN: _proc_event_pass,
    'print': _proc_print_basic
}

def _proc_msg_ref(message, return_dict):
    """process bb refdata message"""
    data = defaultdict(dict)

    if message.hasElement(bn.ERR_RESP):
        raise be.ResponseError(message.getElement(bn.ERR_RESP))
    try:
        msg_type = message.messageType()
        secs = None
        if message.hasElement(bn.SEC_DATA):
                secs = message.getElement(bn.SEC_DATA)
        if secs is not None:
            if msg_type == bn.RESP_REF_DATA:
                for sec in secs.values():
                    sec_id = sec.getElementValue(bn.SEC)
                    data[sec_id].update(_proc_msg_sec(sec, msg_type))
            elif msg_type == bn.RESP_REF_HIST:
                sec_id = secs.getElementValue(bn.SEC)
                data[sec_id] = _proc_msg_sec(secs, msg_type)
            return_dict.update(data)
    except be.SecurityErrors as err:
        print err


def _proc_msg_fld(message, return_dict):
    """process bb field response"""
    if message.hasElement(bn.ERR_FLDSRCH):
        raise be.ResponseError(message.getElement(bn.ERR_FLDSRCH))
    try:
        msg_type = message.messageType()
        if msg_type == bn.RESP_FLD:
            for fld in message.getElement(bn.FLD_DATA).values():
                _proc_msg_flddata(fld, return_dict)
    except be.FieldError as err:
        print err


def _proc_msg_fld_cat(message, return_dict):
    """process bb categorized field response"""
    pass


def _proc_msg_auth(message, __):
    """process bb authorization response"""
    pass


def _proc_msg_auth_logon(message, __):
    """process bb logon response"""
    pass


FUNC_RESPONSE = {
    bn.RESP_REF_HIST: _proc_msg_ref,
    bn.RESP_REF_DATA: _proc_msg_ref,
    bn.RESP_FLD: _proc_msg_fld,
    bn.RESP_FLD_CAT: _proc_msg_fld_cat,
    bn.RESP_AUTH: _proc_msg_auth,
    bn.RESP_LOGON: _proc_msg_auth_logon
}

def _proc_msg_flddata(fld, return_dict):
    """process fieldData"""
    try:
        info = {}
        fld_id = fld.getElementValue(bn.ID)
        if fld.hasElement(bn.ERR_FLD):
            raise be.FieldError(fld.getElement(bn.ERR_FLD), fld_id)

        fld_info = fld.getElement(bn.FLD_INFO)
        mnemonic = fld_info.getElementValue(bn.MNEMONIC)

        return_dict[mnemonic] = info

        info[str(bn.ID)] = fld_id
        info[str(bn.DATA_TP)] = str(fld_info.getElementValue(bn.DATA_TP))

        info[str(bn.CAT_NM)] = []
        for cat in fld_info.getElement(bn.CAT_NM).values():
            info[str(bn.CAT_NM)].append(cat)

        info[str(bn.DESC)] = fld_info.getElementValue(bn.DESC)
        info[str(bn.DOC)] = fld_info.getElementValue(bn.DOC)
        for ppty in fld_info.getElement(bn.PPTY).values():
            if ppty.getElementValue(bn.ID) == bc.FLD_OVDBL:
                info[bc.OVDBL] = ppty.getElementValue(bn.VAL) == 'true'
        info[str(bn.OVDS)] = []
        for ovd in fld_info.getElement(bn.OVDS).values():
            info[str(bn.OVDS)].append(ovd)
        info[str(bn.FTYPE)] = str(fld_info.getElementValue(bn.FTYPE))

    except be.FieldError as err:
        return_dict[fld_id] = info
        info[str(bn.ERR_FLD)] = [err.category, err.message]
        print err


def _proc_msg_sec(sec, msg_type):
    """process bb security"""
    try:
        if sec.hasElement(bn.ERR_SEC):
            raise be.SecurityErrors(sec.getElement(bn.ERR_SEC))
        fld_data = sec.getElement(bn.FLD_DATA)
        if msg_type == bn.RESP_REF_DATA:
            fld_names = expected_fields(fld_data)
            rtn = empty_fld_dict(fld_names)
            if fld_data.numElements() > 0:
                for fld in fld_data.elements():
                    rtn[format_fld_name(fld)] = _proc_msg_sec_data_fld(fld)
        elif msg_type == bn.RESP_REF_HIST:
            rtn = _proc_msg_sec_hist_fld(fld_data)
        if sec.hasElement(bn.EXCS_FLD):
            excs = sec.getElement(bn.EXCS_FLD)
            if excs.numValues() > 0:
                for val in excs.values():
                    fld_id = val.getElementValue(bn.FLD_ID)
                    #if a request has no valid fields, rtn will be a
                    #list so a type error will occur when you try to
                    #set the index
                    try:
                        rtn[format_fld_name(fld_id)] = None
                    except TypeError:
                        rtn = None
                raise be.FieldExceptions(excs)
    except (be.SecurityError, be.FieldExceptions) as err:
        print err
    return rtn


def _proc_msg_sec_data_fld(field):
    """process bb security field data"""
    rtn = []
    if field.datatype() == bc.bdt.SEQUENCE:
        lst = []
        row = None
        for val in field.values():
            if row is None:
                row = create_row_namedtuple(val)
                fld_names = row._fields
            data = empty_fld_dict(fld_names)
            for i, element in enumerate(val.elements()):
                data[format_fld_name(element)] = element.getValue()
            lst.append(row._make([data[f] for f in fld_names]))
        df_idx = [x for x in fld_names if 'DATE' in x.upper()]
        rtn = pd.DataFrame(lst, columns=fld_names)
        rtn = rtn.convert_objects(convert_dates=True,
                                  convert_numeric=True)
        pd.to_datetime(rtn.set_index(df_idx, inplace=True))
        rtn.dropna(how='all', inplace=True)
    else:
        rtn.append(field.getValue())
    try:
        if len(rtn) == 1:
            rtn = rtn[0]
    except Exception as err:
        print err, type(err)
    return rtn


def _proc_msg_sec_hist_fld(field_data):
    """process bb security historical field data"""
    rtn = []
    lst = []
    row = None
    if field_data.numValues() > 0:
        for fld in field_data.values():
            if row is None:
                row = create_row_namedtuple(field_data)
                fld_names = row._fields
            data = empty_fld_dict(fld_names)
            for i, element in enumerate(fld.elements()):
                data[format_fld_name(element)] = element.getValue()
            lst.append(row._make([data[f] for f in fld_names]))
        if len(lst) > 0:
            df_idx = [x for x in fld_names if 'DATE' in x.upper()]
            rtn = pd.DataFrame(lst, columns=fld_names)
            rtn = rtn.convert_objects(convert_dates=True,
                                      convert_numeric=True)
            if df_idx:
                rtn[df_idx] = rtn[df_idx].apply(lambda x:
                                                pd.to_datetime(x))
                rtn.set_index(df_idx, inplace=True)
            rtn.dropna(how='all', inplace=True)
    return rtn


def empty_fld_dict(names):
    """creates a dictionary with expected field names initialized to
    none
    """
    return {_f:None for _f in names}


def expected_fields(element):
    """returns a list of expected field names"""
    el_def = element.elementDefinition()
    el_typ = el_def.typeDefinition()
    if el_typ.numElementDefinitions() > 0:
        els = el_typ.elementDefinitions()
    else:
        els = element.elements()
    names = map(format_fld_name, els)
    return names


def create_row_namedtuple(element):
    """self explanotory"""
    names = expected_fields(element)
    row = namedtuple('row', names, rename=True)
    return row
