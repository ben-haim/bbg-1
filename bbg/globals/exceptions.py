# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 11:09:40 2014

@author: Brian
"""

import bbg.globals.names as bn
from blpapi.exception import (DuplicateCorrelationIdException,
                              FieldNotFoundException, IndexOutOfRangeException,
                              InvalidArgumentException,
                              InvalidConversionException,
                              InvalidStateException, NotFoundException,
                              UnknownErrorException,
                              UnsupportedOperationException)


class Error(Exception):
    """Base class for module exceptions"""
    def __init__(self, msg=''):
        super(Error, self).__init__(msg)


class _elementError(Error):
    """Base bloomberg element error"""
    def __init__(self, errElement):
        super(_elementError, self).__init__('')
        self.source = errElement.getElementValue(bn.SRC)
        self.code = errElement.getElementValue(bn.CODE)
        self.category = errElement.getElementValue(bn.CAT)
        self.message = errElement.getElementValue(bn.MSG)
        self.subcategory = ''
        if errElement.hasElement(bn.SUBCAT):
            self.subcategory = errElement.getElementValue(bn.SUBCAT)


    def __str__(self):
        return ('{0}: {1}({2}) - {3}'.format(self.__class__.__name__,
                self.category, self.subcategory, self.message))


class _errorContainer(Error):
    """Base container for error elements which potentially
    containing multiple errors
    """
    def __init__(self, errCont, errType=None):
        super(_errorContainer, self).__init__('')
        self.errors = []
        if errType is None:
            errType = _elementError

        if errCont.isArray():
            for err in errCont.values():
                self.errors.append(errType(err))
        else:
            self.errors.append(errType(errCont))

    def __str__(self):
        return '\n'.join([str(e) for e in self.errors])


class SessionError(Error):
    """Base class for module exceptions"""
    pass


class InputError(Error):
    """generic input error for when inputs fail"""
    pass


class ResponseError(_elementError):
    pass


class FieldSearchError(_elementError):
    pass


class SecurityError(_elementError):
    pass


class SecurityErrors(_errorContainer):
    def __init__(self, errCont):
        super(SecurityErrors, self).__init__(errCont, SecurityError)


class FieldError(_elementError):
    def __init__(self, errElement, field_id):
        super(FieldError, self).__init__(errElement)
        self.fieldId = field_id


class FieldException(_elementError):
    """Bloomberg fieldException"""
    def __init__(self, errElement):
        super(FieldException, self).__init__(
              errElement.getElement(bn.INFO_ERR))
        self.fieldId = errElement.getElementValue(bn.FLD_ID)
        self.field_msg = ''
        if errElement.hasElement(bn.MSG):
            self.field_msg = errElement.getElementValue(bn.MSG)

    def __str__(self):
        return ('{0}({1}): {2}({3}) - {4}'.format(
                self.__class__.__name__, self.fieldId, self.category,
                self.subcategory, self.message))


class FieldExceptions(_errorContainer):
    """container for multiple fieldExceptions"""
    def __init__(self, errCont):
        super(FieldExceptions, self).__init__(errCont, FieldException)


def main():
    """main function..."""
    try:
        raise Error('success')
    except Error as err:
        print err


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Ctrl+C pressed. Stopping..."