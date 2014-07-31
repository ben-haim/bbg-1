# -*- coding: utf-8 -*-

"""
Created on Wed Jun 04, 2014

@author: Brian Jacobowski <bjacobowski.dev@gmail.com>
"""

import bbg.globals.constants as bc
import bbg.globals.exceptions as be
import bbg.globals.names as bn
import bbg.bloomberg.session as bs
from bbg.utils.date import BbgDate
from bbg.utils.misc import shape_list
from bbg.globals.fields import CUSIP

import blpapi as bb
import datetime as dt
import pandas as pd
from collections import namedtuple, defaultdict
from itertools import product

IDS =  bc.IDS
FLDS = bc.FLDS
OVDS = bc.OVDS

TODAY = dt.date.today()
LAST_MONTH = TODAY - dt.timedelta(30)

OvdNamedTuple = namedtuple('override', 'fieldId, value')


def get_data_bbg(identifiers,
                 fields,
                 overrides=None):
    """function to request static data from bloomberg, returns a
    dictionary of results with tables stored as pandas DataFrames

    Parameters
    ----------
    identifiers : list-like object of bloomberg identifiers of the form
        'symbol [exchange] <yellow key>'. Symbol can be ticker/name/
        cusip/etc.

    fields : list-like object of bloomberg field mnemonics or CALCRT ID.
        Although either can be input, only the mnemonic will be output.

    overrides : list-like object of tuples or dictionary. Tuples must be of
        the form [(fieldId, value), ], while dictionaries are
        {fieldId: value, }.
        FieldId(s) are mnemonics or CALCRT IDs, values will be converted
        to the proper type if possible.

    Examples
    --------
    >>> ids = ['googl us equity', 'aapl us equity', 'msft us equity']
    >>> flds = ['PX_LAST', 'PX_VOLUME', 'SETTLE_DT']
    >>> ovds = [('SETTLE_DT','01-01-2014')]
    >>> b = get_data_bbg(ids, flds, ovds)
    """
    inputs = locals().copy()
    rtn = None
    with bs.Session() as session:
        _ref_req_queue(session, 1, inputs)
        _refdata_to_bloomberg(session)
        session.queue.join()
        rtn = session.correlation_ids[1]
    return rtn


def get_multidata_bbg(requests):
    """function for multiple asynchronous refdata requests, returns a
    dictionary of the form correlationID:result.

    Function Parameters
    ----------
    requests : dictionary of correlationID:request pairs. CorrelationIDs
        are unique integers (cannot reuse until previous requests have
        returned). Requests can be either dicts of named arguments or
        list-likes of ordered arguments. Although technically anything
        can be made into a blpapi.CorrelationId, integers simplify usage.

    Request Parameters
    ----------
    identifiers : list-like object of bloomberg identifiers of the form
        'symbol [exchange] <yellow key>'. Symbol can be ticker/name/
        cusip/etc.

    fields : list-like object of bloomberg field mnemonics or CALCRT ID.
        Although either can be input, only the mnemonic will be output.

    overrides : list-like object of tuples or dictionary. Tuples must be of
        the form [(fieldId, value), ], while dictionaries are
        {fieldId: value, }.
        FieldId(s) are mnemonics or CALCRT IDs, values will be converted
        to the proper type if possible.
    """
    with bs.Session() as session:
        try:
            if not isinstance(requests, dict):
                raise be.InputError('request_mult_refdata requires a '
                    'dictionary of correlationId:input pairs')
            for corr_id, req in requests.items():
                if isinstance(req, dict):
                    inputs = req
                elif hasattr(req, '__iter__'):
                    if len(req) == 3:
                        pass
                    elif len(req) == 2:
                        req = list(req)
                        req.append(None)
                    else:
                        raise be.InputError('Request {0} has {1} items'
                            ', expected 2-3.'.format(corr_id, len(req)))
                    inputs = dict(zip((IDS, FLDS, OVDS), req))
                else:
                    raise be.InputError('Request {0} is of type: {0}, '
                        'expected dict or list-like'.format(corr_id,
                                                            type(req)))
                _ref_req_queue(session, corr_id, inputs)
        except be.InputError as err:
            print err
        _refdata_to_bloomberg(session)
        session.queue.join()
        rtn = session.correlation_ids
    return rtn


def get_sensitivity_bbg(identifier,
                        dependent,
                        independents,
                        values,
                        overrides=None):
    """function for calculating sensitivities on a dependent field.
    Returns a pandas DataFrame of results.

    Parameters
    ----------
    identifier : bloomberg identifier of the form symbol [exchange]
        <yellow key>'. Symbol can be ticker/name/cusip/etc.

    dependent : bloomberg field mnemonics or CALCRT ID. This is the
        field for which you want results

    independents : list-like object of bloomberg field mnemonics or
        CALCRT ID.  These are the fields you would like to override.
        Function supports 1-3 independent variables.

    values : list-like object of list-likes containing the override
        values for the independent fields. Must have the same number
        of list-likes as there are independents.

    overrides : list-like object of tuples or dictionary. Tuples must
        be of the form [(fieldId, value), ], while dictionaries are
        {fieldId: value, }. FieldId(s) are mnemonics or CALCRT IDs,
        values will be converted to the proper type if possible. If
        an independent field is also included in the overrides list,
        the override will be ignored.

    Examples
    --------
    >>> import numpy as np
    >>> sec = 'CT10 Govt'
    >>> dep = 'YLD_CNV_BID'
    >>> inds = ['PX_BID', 'SETTLE_DT']
    >>> px = get_data_bbg(sec, 'PX_LAST')
    >>> pxs = px * np.arange(0.9,1.1,0.05)
    >>> settle = get_data_bbg(sec, 'SETTLE_DT')
    >>> settles = [settle, settle + datetime.timedelta(30)]
    >>> vals = [pxs, settles]
    >>> data = get_sensitivity_bbg(sec, dep, inds, vals)
    """
    try:
        if not isinstance(identifier, str):
            raise be.InputError('Expected a single bloomberg identifier of '
                                'string type, got {0}'.format(
                                type(identifier)))
        if not isinstance(dependent, str):
            raise be.InputError('Expected a single bloomberg field of '
                                'string type for dependent, got {0}'.format(
                                type(identifier)))
        if (not hasattr(independents, '__iter__') and
            not all( isinstance(x, str) for x in independents)):
            raise be.InputError('Expected a list-like of  bloomberg fields of '
                                'string type for independents, got {0}'.format(
                                [type(x) for x in identifier]))
        if not all(hasattr(val, '__iter__') for val in values):
            raise be.InputError('Expected a list-like of override values for '
                                'values, got {0}'.format(type(values)))
        if not len(independents) == len(values):
            raise be.InputError('Must have the same number of independents '
                                'and list-likes of values')
        try:
            ovds_base = {key.replace(' ', '_').upper(): val for
                         key, val in dict(overrides).items()}
        except TypeError:
            raise be.InputError('overrides must be convertible to a dict')
    except be.InputError as err:
        print err
    sec_id = identifier.upper()
    fld = dependent.upper()
    flds = list(_sorted_unq_tuple([fld, 'NAME'] + list(independents)))
    #Create a list of dicts with all the combinations of independent/value
    #override pairs. These dicts are then used to update the base override.
    if len(independents) > 1:
        inds = [[ind.replace(' ', '_').upper()] for ind in independents]
    scens = [dict(x) for x in product( *map(product, inds, values))]

    #Create the requests dictionary for input into get_multidata_bbg
    reqs = {}
    for i, scen in enumerate(scens):
        ovds = ovds_base.copy()
        ovds.update(scen)
        reqs[i] = {IDS: sec_id, FLDS: flds, OVDS: ovds}
    results = get_multidata_bbg(reqs)
#    results = multi_thrd(reqs)
    # rtn_arr = []
    rtn_df = []
    for x in xrange(len(scens)):
        ovds = {ovd[0].replace(' ', '_').upper():ovd[1]
                for ovd in reqs[x][OVDS]}
        res = results[x][sec_id]
        # rtn_arr.append(res[fld])
        res.update(ovds)
        rtn_df.append(res)
    rtn_df = pd.DataFrame(rtn_df)
    # rtn_df = [x.update(reqs[i].update({CUSIP:sec_id})) for
    #           i, x in enumerate(rtn_df)]
    # rtn_df = pd.DataFrame(rtn_df)

    # arr_sz = [len(x) for x in values]
    # rtn_arr = shape_list(rtn_arr, arr_sz)

    return rtn_df


def get_histdata_bbg(identifiers,
                     fields,
                     overrides=None,
                     startDate=LAST_MONTH,
                     endDate=TODAY,
                     periodicityAdjustment=None,
                     periodicitySelection=None,
                     currency=None,
                     overrideOption=None,
                     pricingOption=None,
                     nonTradingDayFillOption=None,
                     nonTradingDayFillMethod=None,
                     maxDataPoints=None,
                     returnEids=None,
                     returnRelativeDate=None,
                     adjustmentNormal=None,
                     adjustmentAbnormal=None,
                     adjustmentSplit=None,
                     adjustmentFollowDPDF=None,
                     calendarCodeOverride=None,
                     calendarOverrides=None,
                     calendarOverridesOperation='CDR_AND'):
    """function to request historical data from bloomberg,
    returns a dictionary of results with tables stored as pandas DataFrames.

    Parameters
    ----------
    identifiers : list-like object of bloomberg identifiers of the form
        'symbol [exchange] <yellow key>'. Symbol can be ticker/name/
        cusip/etc.

    fields : list-like object of bloomberg field mnemonics or CALCRT ID.
        Although either can be input, only the mnemonic will be output.

    overrides : list-like object of tuples or dictionary. Tuples must be of
        the form [(fieldId, value), ], while dictionaries are
        {fieldId: value, }.
        FieldId(s) are mnemonics or CALCRT IDs, values
        will be converted to the proper type if possible.

    startDate : date/datetime/str object, default 1 month before today.

    endDate : date/datetime/str object, default today.

    Optional keyword arguments (default to bloomberg defaults if None)
    ----------
    periodicityAdjustment : str, [ACTUAL/CALENDAR/FISCAL], default None.

    periodicitySelection : str, [DAILY/WEEKLY/MONTHLY/QUARTERLY/SEMI_ANUALLY/
        YEARLY], default None.

    currency : str, 3 letter ISO currency code, e.g. USD or GBP, default None.

    overrideOption : str, [OVERRIDE_OPTION_CLOSE/OVERRIDE_OPTION_GPA],
        default None.

    pricingOption : str, [PRICING_OPTION_PRICE/PRICING_OPTION_YIELD],
        default None.

    nonTradingDayFillOption : str, [NON_TRADING_WEEKDAYS/ALL_CALENDAR_DAYS/
        ACTIVE_DAYS_ONLY], default None.

    nonTradingDayFillMethod : str, [PREVIOUS_VALUE/NIL_VALUE], default None.

    maxDataPoints : int, response will contain up to x data points. If the
        original data set is larger than x, the response will be a subset
        containing the x most recent data points, default None.

    returnEids : bool, default None.

    returnRelativeDate : bool, default None.

    adjustmentNormal : bool, Adjust historical pricing to reflect: Regular
        Cash, Interim, 1st Interim, 2nd Interim, 3rd Interim, 4th Interim,
        5th Interim, Income, Estimated, Partnership Distribution, Final,
        Interest on Capital, Distribution, Prorated, default None.

    adjustmentAbnormal : bool, Adjust historical pricing to reflect: Special
        Cash, Liquidation, Capital Gains, Long-Term Capital Gains, Short-Term
        Capital Gains, Memorial, Return of Capital, Rights Redemption,
        Miscellaneous, Return Premium, Preferred Rights Redemption,
        Proceeds/Rights, Proceeds/Shares, Proceeds/Warrants, default None.

    adjustmentSplit : bool, Adjust historical pricing and/or volume to
        reflect: Spin-Offs, Stock Splits/Consolidations, Stock Dividend/Bonus,
        Rights Offerings/Entitlement, default None.

    adjustmentFollowDPDF : bool, Setting to true will follow the DPDF<GO>
        BLOOMBERG PROFESSIONAL service function, default True.

    calendarCodeOverride : str, CDR <GO> calendar type. Returns the data
        based on the calendar of the specified country, exchange, or religion
        from CDR<GO>. Taking a two character calendar code null terminated
        string. This will cause the data to be aligned according to the
        calendar and including calendar holidays. Only applies only to DAILY
        requests, default None.

    calendarOverrides : str-array, CDR <GO> calendar type. Accepts a
        two-character calendar code null-terminated string of multiple
        country, exchange, or religious calendars from CDR<GO>. This will
        cause the data to be aligned according to the set calendar(s)
        including their calendar holidays. Only applies to DAILY requests.

    calendarOverridesOperation='CDR_AND : str, [CDR_AND/CDR_OR]. CDR_AND
        returns the intersection of trading days. That is, a data point is
        returned if a date is a valid trading day in all calendar codes
        specified in the request. CDR_OR returns the union of trading days.
        That is, a data point is returned if a date is a valid trading day
        for any of the calendar codes specified in the request, default
        CDR_AND.


    Examples
    --------
    >>> ids = ['googl us equity', 'aapl us equity', 'msft us equity']
    >>> flds = ['PX_LAST', 'PX_VOLUME']
    >>> st_dt = dt.datetime(2013, 1, 1)
    >>> end_dt = dt.datetime.today()
    >>> b = request_refdata(ids, flds, startDate=st_dt, endDate=end_dt)

    """
    inputs = locals().copy()
    rtn = None
    inputs['startDate'] = BbgDate.from_unknown_type(startDate).str_to_bbg()
    inputs['endDate'] = BbgDate.from_unknown_type(endDate).str_to_bbg()
    inputs.update(_ref_req_inputs(inputs))
    with bs.Session() as session:
        cid = bb.CorrelationId(1)
        req = _get_request(session, bc.SVC_REF, bc.REQ_REF_HIST)
        _ref_req_base(req, inputs)

        processed_list = [IDS, FLDS, OVDS]
        for item in processed_list:
            inputs.pop(item, None)

        cal_ovds = inputs.pop('calendarOverrides', None)
        cal_ovds_op = inputs.pop('calendarOverridesOperation', None)

        _req_set_elements(req, inputs)
        _add_calendar_overrides(req, cal_ovds, cal_ovds_op)

        session.queue.put((cid, req))
        _refdata_to_bloomberg(session)
        session.queue.join()
        rtn = session.correlation_ids[1]
    return rtn


def get_fldinfo_bbg(fields):
    """function for retrieving bloomberg field information, including
    available override fields. Returns a dictionary of the form field:result.
    Result is a dictionary containing mnemonic, description, datatype,
    documentation, category name, overridable, and a dictionary of available
    overrides with the same information. Function only retrieves detailed
    info on one level of available overrides.

    Parameters
    ----------
    fields : list-like object of bloomberg field mnemonics or CALCRT ID.
        Although either can be input, only the mnemonic will be output.
    """
    corr_id = 1
    with bs.Session() as session:
        _flds_info_queue(session, corr_id, fields)
        _refdata_to_bloomberg(session)
        session.queue.join()
        rtn = session.correlation_ids[corr_id]
        for fld, info in rtn.items():
            if info.get(OVDS, None):
                _flds_info_queue(session, fld, info[OVDS])
        _refdata_to_bloomberg(session)
        session.queue.join()
        for fld, info in rtn.items():
            if info.get(OVDS, None):
                info[OVDS] = session.correlation_ids[fld]
    return rtn


def _refdata_to_bloomberg(session):
    """Send refdata requests to bloomberg."""
    while session.queue.qsize() > 0:
        correlation_id, req = session.queue.get()
        try:
#            print 'Sending to bloomberg...', req
            session.sendRequest(req, correlationId=correlation_id)
        except Exception as err:
            print err


def _ref_req_queue(session, correlation_id, inputs):
    """Interface between single/multiple refdata request functions and
    _refdata_to_bloomberg. This function creates the queue which
    _refdata_to_bloomberg then pulls from to send. You then queue.join()
    in the calling function to wait for asynchronous results to get back
    """
    fields = inputs[FLDS]
    if hasattr(fields, '__iter__'):
        flds = tuple(fields) + ('ID_CUSIP',)
    else:
        flds = (fields, 'ID_CUSIP')
    inputs[FLDS] = flds

    inputs.update(_ref_req_inputs(inputs))
    req = _get_request(session, bc.SVC_REF, bc.REQ_REF_DATA)
    _ref_req_base(req, inputs)
    cid = bb.CorrelationId(correlation_id)

    session.queue.put((cid, req))


def _flds_info_queue(session, correlation_id, fields):
    """build a FieldInformationRequest, add to the request queue"""
    req = _get_request(session, bc.SVC_FLDS, bc.REQ_FLD_INFO)
    ids = req.getElement(bn.ID)

    flds = _sorted_unq_tuple(fields, '_')
    _append_value(ids, flds, "Error with Field input values")

    req.append('properties', 'fieldoverridable')
    req.set("returnFieldDocumentation", True)

    cid = bb.CorrelationId(correlation_id)

    session.queue.put((cid, req))


def _ref_req_inputs(inputs):
    """normalize base inputs - tuples used to allow memoization"""
    try:
        rtn = {}
        rtn[IDS] = _sorted_unq_tuple(inputs[IDS])
        rtn[FLDS] = _sorted_unq_tuple(inputs[FLDS], '_')
        rtn[OVDS] = None
        overrides = inputs.get(OVDS, None)
        if overrides is not None:
            try:
                if type(overrides) == dict:
                    rtn[OVDS] = tuple(sorted({OvdNamedTuple(f, v)
                                      for f, v in overrides.items()},
                                      key=lambda fld: fld.fieldId))
                elif (len(overrides) == 2 and
                      all(not hasattr(x, '__iter__') for x in overrides)):
                    rtn[OVDS] = (OvdNamedTuple(overrides[0],
                                                     overrides[1]),)
                else:
                    rtn[OVDS] = tuple(sorted({OvdNamedTuple(f, v)
                                      for f, v in overrides},
                                      key=lambda fld: fld.fieldId))
            except Exception as err:
                print err
    except Exception as err:
        print err
    return rtn


def _get_request(session, service_name, req_type):
    """get bloomberg refdata service"""
    service = session.getService(service_name)
    req = service.createRequest(req_type)
    return req


def _ref_req_base(request, inputs):
    """add the base inputs to refdata request"""
    secs = request.getElement(bn.SECS)
    _append_value(secs, inputs[IDS], "Error with Identifier input values")

    flds = request.getElement(bn.FLDS)
    _append_value(flds, inputs[FLDS], "Error with Field input values")

    if inputs.get(OVDS) is not None:
        ovds = request.getElement(bn.OVDS)
        _append_overrides(ovds, inputs[OVDS])


def _append_value(element, values, err_msg=''):
    """append values to request"""
    try:
        map(element.appendValue, values)
    except Exception as err:
        print err
        raise be.InputError(err_msg)


def _append_overrides(ovds_elem, overrides):
    """append overrides to request"""
    def _add_ovd(ovd_tuple):
        """append override to overrides"""
        ovd = ovds_elem.appendElement()
        ovd.setElement(bn.FLD_ID, ovd_tuple.fieldId)
        ovd.setElement(bn.VAL, ovd_tuple.value)

    try:
        if overrides is not None:
            map(_add_ovd, overrides)
    except Exception as err:
        print err
        raise be.InputError("Error with Override input values")


def _add_calendar_overrides(request,
                            ovds_lst=(),
                            ovds_op='CDR_AND'):
    """"append calendar overrides to historical request"""
    try:
        if ovds_lst:
            cdr_ovds_info = request.getElement(bn.CAL_OVDS_INFO)
            cdr_ovds_info.setElement(bn.CAL_OVDS_OP, ovds_op)
            cdr_ovds = cdr_ovds_info.getElement(bn.CAL_OVDS)
            for ovd in ovds_lst:
                cdr_ovds.appendValue(ovd)
    except Exception as err:
        print err
        raise be.InputError("Error with Calendar Override input values")


def _req_set_elements(request, kw_dict):
    """set element values for request"""
    for key, val in kw_dict.items():
        if val is not None:
            request.set(bb.Name(key), val)


def _sorted_unq_tuple(itr, replace_spaces=None):
    """Creates a tuple of unique sorted strings by making a tuple from
    a sorted set comprehension. Provides the option to replace spaces with
    the supplied character.
    """
    rtn = None
    try:
        if replace_spaces:
            if hasattr(itr, '__iter__'):
                rtn = tuple(sorted({x.replace(' ', replace_spaces).upper()
                            for x in itr}))
            else:
                rtn = (str(itr).replace(' ', replace_spaces).upper(),)
        else:
            if hasattr(itr, '__iter__'):
                rtn = tuple(sorted({x.upper() for x in itr}))
            else:
                rtn = (str(itr).upper(),)
    except Exception as err:
        print err, type(err)
    return rtn


def main():
    """main function..."""

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Ctrl+C pressed. Stopping..."
