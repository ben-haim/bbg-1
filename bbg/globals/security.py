__author__ = 'Brian'

"""
"""

from bbg.bloomberg.misc import get_bbg_ids
import bbg.globals.fields as bf

class Security(object):
    """
    """
    def __init__(self, identifier):
        id_info = get_bbg_ids(identifier)
        self.cusip = id_info[bf.CUSIP]
        self.name = id_info[bf.NAME]
        self.sector = id_info[bf.SECTOR]
        self.ticker = id_info[bf.TICKER]
        self.parse_key = id_info[bf.PARSE_KEY]
        self.identifier = identifier


class Bond(Security):
    """
    """
    def __init__(self, identifier):
        super(self.__class__, self).__init__(identifier)



class Equity(Security):
    """
    """
    def __init__(self, identifier):
        super(self.__class__, self).__init__(identifier)


class MtgeBond(Bond):
    """
    """
    def __init__(self, identifier, **kwargs):
        super(self.__class__, self).__init__(identifier)
        self.prepay_type = kwargs.get(bf.MTG_PP_TYP, 'CPR')
        self.prepay_vector = kwargs.get(bf.MTG_PP_VECT)
        self.prepay_multiples = []
        self.px = kwargs.get(bf.PX_B)


class ClosedEndFund(Equity):
    """
    """
    def __init__(self, identifier):
        super(self.__class__, self).__init__(identifier)
