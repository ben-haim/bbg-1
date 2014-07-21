# -*- coding: utf-8 -*-
"""
"""

from bbg import get_data_bbg
import bbg.globals.fields as bf

import pandas as pd
from collections import defaultdict

def get_bbg_ids(identifiers):
    """Function to parse. Retrieves identification info from bloomberg.
    """
    flds = [bf.CUSIP, bf.TICKER, bf.NAME, bf.SECTOR, bf.PARSE_KEY]
    rtn = get_data_bbg(identifiers, flds)
    if len(rtn) == 1:
        rtn = rtn.values()[0]
    return rtn
