# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 10:36:44 2014

@author: Brian
"""

def _get_ip_address():
    """get computer's ip address"""
    import socket
    return socket.gethostbyname(socket.gethostname())
