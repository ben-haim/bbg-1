# -*- coding: utf-8 -*-
"""
Created on Tue Jul 08 08:54:04 2014

@author: Brian Jacobowski <bjacobowski.dev@gmail.com>
"""

from blpapi.element import Element
from blpapi.schema import SchemaElementDefinition


def format_fld_name(fld_name):
    """Reformats input field name to match bloomberg's expected style,
    uppercase with underscores, no spaces.
    """
    if isinstance(fld_name, str):
        rtn = fld_name.replace(' ', '_').upper()
    elif isinstance(fld_name, (Element, SchemaElementDefinition)):
        rtn = str(fld_name.name()).replace(' ', '_').upper()
    else:
        rtn = str(fld_name).replace(' ', '_').upper()
    return rtn


def shape_list(list_in, shape):
    rtn = list_in[:]
    for x in reversed(shape):
        args = [iter(rtn)] * x
        rtn = map(list, zip(*args))
    return rtn
