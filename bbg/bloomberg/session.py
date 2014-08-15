# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 16:54:37 2014

@author: Brian Jacobowski
"""

import blpapi as bb
import bbg.globals.constants as bc
import bbg.globals.exceptions as be
import bbg.bloomberg.response as br
from bbg.utils.decorators import ignored
from optparse import OptionParser
from collections import defaultdict
from Queue import Queue
import multiprocessing

def _parse_cmd_line():
    """adds options to the command line option parser"""
    parser = OptionParser()

    parser.add_option("-a",
                      "--ip",
                      dest="host",
                      help="server name or IP (default: %default)",
                      metavar="ipAddress",
                      default="localhost")
    parser.add_option("-p",
                      dest="port",
                      type="int",
                      help="server port (default: %default)",
                      metavar="tcpPort",
                      default=8194)

    options, __ = parser.parse_args()
    return options


class _SessionOptions(bb.SessionOptions):
    """set generic bloomberg session options"""
    def __init__(self):
        self.options = _parse_cmd_line()
        super(self.__class__, self).__init__()
        self.setServerHost(self.options.host)
        self.setServerPort(self.options.port)

SESSION_OPTIONS = _SessionOptions()


# class MultiProcessSession(multiprocessing.Process):
#     def __init__(self):
#         multiprocessing.Process.__init__(self)
#         self.session = None
#         # self.start()
#
#     def run(self):
#         self.session = Session()
#
#     # def __enter__(self):
#     #     """pass"""
#     #     return self
#     #
#     # def __exit__(self, exc_type, exc_val, exc_tb):
#     #     self.session.__exit__(self.session, exc_type, exc_val, exc_tb)
#     #     super(MultiProcessSession, self).terminate()


class Session(bb.Session):
    """sub-class adding functionality to blpapi.Session. Automatically
    starts an asynchronous session with an event handler and dispatcher.
    Request data can be retrieved through the Session.correlation_ids
    dictionary
    """
    def __init__(self, handler=None):
        self.correlation_ids = defaultdict(dict)
        if handler is None:
            handler = br.processEvent
        self.event_handler = handler
        self.dispatcher = bb.EventDispatcher(4)
        super(Session, self).__init__(SESSION_OPTIONS,
                                      self.event_handler,
                                      self.dispatcher)
        self.dispatcher.start()
        self.started = False
        self.queue = Queue()
        self.subscription_list = bb.SubscriptionList()
        self.start_session()

    def start_session(self):
        """Starts an asynchronous session, relies on the event handler
        to signify that the session was successfully started
        """
        try:
            self.queue.put(0)
            __ = bb.Session.startAsync(self)
            self.queue.join()
        except be.SessionError as err:
            print err

#     def run(self):
#         while True:
#             correlation_id, req = self.queue.get()
#         try:
# #            print 'Sending to bloomberg...', req
#             self.sendRequest(req, correlationId=correlation_id)
#         except Exception as err:
#             print err


    def getService(self, service_name):
        """overrides the bb function to open/get service in one step"""
        rtn = None
        try:
            rtn = super(self.__class__, self).getService(service_name)
        except be.NotFoundException as err:
            try:
                if not self.started:
                    self.start_session()
                if not self.openService(service_name):
                    raise be.SessionError("Failed to open {0}".format(
                                       service_name))
                rtn = super(self.__class__,
                                self).getService(service_name)
                if rtn is None:
                    raise be.SessionError('Failed to get service')
            except (be.SessionError, be.NotFoundException) as err:
                print err
        return rtn


    def __enter__(self):
        """pass"""
        return self


    def __exit__(self, etype, value, traceback):
        """shut down the session and its event handler"""
        try:
            if self.subscription_list is not None:
                with ignored(Exception):
                    self.unsubscribe(self.subscription_list)
            #Tried manually stopping the event dispatcher, it slowed
            #functionality significantly
            self.dispatcher = None
            self.event_handler = None
            # self = None
            if self.event_handler is None:
                with ignored(Exception):
                    self.stop()
            else:
                with ignored(Exception):
                    self.stopAsync()
            self = None
        finally:
            pass


def main():
    """main function..."""
    with Session() as session:
        svc = session.getService(bc.SVC_REF)
        print svc
        print 'done'


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print "Ctrl+C pressed. Stopping..."
