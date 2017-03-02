# -*- coding: utf-8 -*-

"""
backend.globals
~~~~~~~~~~~~~~~

This module save all global objects in backend.

:copyright: (c) 2016 by AgileNet.
"""
import os
from collections import namedtuple


class Global(object):
    BackendConfig = namedtuple('BackendConfig', ['log_enable',
                                                 'log_level',
                                                 'print_enable',
                                                 'print_level',
                                                 'session_hsize',
                                                 'session_lifetime',
                                                 'user_hsize',
                                                 'manage_eth',
                                                 'engineer',
                                                 'engineer_passwd',
                                                 'senior',
                                                 'senior_passwd',
                                                 'http_port',
                                                 'https_port',
                                                 'dev_model',
                                                 'heartbeat_port',
                                                 'tm_rpc_port',
                                                 'sm_rpc_port',
                                                 'pm_rpc_port',
                                                 'pppserv_rpc_port',
                                                 'pg_rpc_port',
                                                 'monitor_rpc_port',
                                                 'log_rpc_port',
                                                 'inband_rpc_port',
                                                 'pppc_rpc_port',
                                                 'log_listen_port',
                                                 'pid',
                                                 'version'])
    BackendConfig.pid = os.getpid()
    with open('./backend/__version__') as f:
        BackendConfig.version = f.read().rstrip().lstrip()

    ##############################################################
    Sessions = dict()
    """
    session = {
        'username': username,
        'ip': ip,
        'port': port,
        'mode': return_data['admin_mode'],
        'last_operate_time': time.time()
    }
    """
    ##############################################################
    Users = dict()
    """
    username = {
        'password': password,
        'authority': authority
    }
    """