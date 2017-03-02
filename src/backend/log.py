# -*- coding: utf-8 -*-

"""
backend.log
~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import os
import ctypes
from pprint import pprint

from .config import Config
from .globals import Global


LOG_EMERG = 0
LOG_ALERT = 1
LOG_CRIT = 2
LOG_ERR = 3
LOG_WARNING = 4
LOG_NOTICE = 5
LOG_INFO = 6
LOG_DEBUG = 7

if not os.path.exists('./backend/lib/liblog.so'):
    raise Exception('backend/lib/liblog.so not found!')

liblog = ctypes.cdll.LoadLibrary('./backend/lib/liblog.so')


def start_log():
    ret = liblog.start_log_agent(
        ctypes.c_ubyte(9),
        ctypes.c_int(Global.BackendConfig.pid),
        ctypes.c_char_p('127.0.0.1'.encode()),
        ctypes.c_ushort(Global.BackendConfig.log_listen_port))

    if ret != 0:
        raise Exception('Start log agent failed!')

    liblog.reload_debug_info(
        ctypes.c_ubyte(Global.BackendConfig.print_enable),
        ctypes.c_ubyte(Global.BackendConfig.print_level),
        ctypes.c_ubyte(Global.BackendConfig.log_enable),
        ctypes.c_ubyte(Global.BackendConfig.log_level))


def operate(msg, client_id):
    msg = '{0}[{1}:{2}]: {3}'.format(
        Global.Sessions[client_id]['username'],
        Global.Sessions[client_id]['ip'],
        Global.Sessions[client_id]['port'],
        msg.encode())

    liblog.log_record_advanced(
        ctypes.c_ubyte(0),
        ctypes.c_ubyte(16),
        ctypes.c_char_p(msg.encode()))
   

def alarm(msg):
    liblog.log_record_advanced(ctypes.c_ubyte(1),
                               ctypes.c_ubyte(32),
                               ctypes.c_char_p(msg.encode()))