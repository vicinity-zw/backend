# -*- coding: utf-8 -*-

"""
backend.config
~~~~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import os
import json
import xml.etree.ElementTree

from .globals import Global


class Config(object):
    # Program path
    PROGRAM_PATH = '/home/GreeNet/vMSE/'
    # Config file path
    CONFIG_FILE_PATH = PROGRAM_PATH + 'config/backend/backend.xml'
    # WebUI path
    WEB_UI_PATH = '/var/www/vmse/'
    # Backend telnet port
    TELNET_PORT = 51106
    # Backend telnet password
    TELNET_PASSWORD = '123456'
    # share.xml's path, used to get port info
    SHARE_XML_PATH = PROGRAM_PATH + 'config/share.xml'
    # User account path
    USER_PATH = PROGRAM_PATH + 'config/backend/user.json'



class ParseConfig(object):
    """Parse backend.xml and share.xml"""
    @classmethod
    def parse(self):
        ###################################################################
        if not os.path.exists(Config.CONFIG_FILE_PATH):
            raise Exception('\nbackend.xml not found!')

        try:
            tree = xml.etree.ElementTree.parse(Config.CONFIG_FILE_PATH)
        except:
            raise Exception('\nbackend.xml format error!')
        root = tree.getroot()

        Global.BackendConfig.log_enable = int(find_element(tree, 'log_enable'))
        Global.BackendConfig.log_level = int(find_element(tree, 'log_level'))
        Global.BackendConfig.print_enable = int(find_element(tree, 'printf_enable'))
        Global.BackendConfig.print_level = int(find_element(tree, 'printf_level'))
        Global.BackendConfig.session_hsize = int(find_element(tree, 'Session_hsize'))
        Global.BackendConfig.session_lifttime = int(find_element(tree, 'Session_lifetime'))
        Global.BackendConfig.user_hszie = int(find_element(tree, 'User_hsize'))
        Global.BackendConfig.manage_eth = find_element(tree, 'manage_eth')
        Global.BackendConfig.engineer = find_element(tree, 'engineer')
        Global.BackendConfig.engineer_passwd = find_element(tree, 'engineer_passwd')
        Global.BackendConfig.senior = find_element(tree, 'senior', enable_empty=True)
        Global.BackendConfig.senior_passwd = find_element(tree, 'senior_passwd', enable_empty=True)
        Global.BackendConfig.http_port = int(find_element(tree, 'http_port'))
        Global.BackendConfig.https_port = int(find_element(tree, 'https_port'))
        Global.BackendConfig.dev_model = find_element(tree, 'dev_model')

        ###################################################################
        if not os.path.exists(Config.SHARE_XML_PATH):
            raise Exception('\nshare.xml not found!')

        try:
            tree = xml.etree.ElementTree.parse(Config.SHARE_XML_PATH)
        except:
            raise Exception('\nshare.xml format error!')
        port_info = tree.find('port_info')

        Global.BackendConfig.heartbeat_port = int(find_element(port_info, 'monitor_port_info/backend_mn_port'))
        Global.BackendConfig.tm_rpc_port = int(find_element(port_info, 'backend_port_info/tm_rpc_port'))
        Global.BackendConfig.sm_rpc_port = int(find_element(port_info, 'backend_port_info/sm_rpc_port'))
        Global.BackendConfig.pm_rpc_port = int(find_element(port_info, 'backend_port_info/pm_rpc_port'))
        Global.BackendConfig.pppserv_rpc_port = int(find_element(port_info, 'backend_port_info/pppserv_rpc_port'))
        Global.BackendConfig.pg_rpc_port = int(find_element(port_info, 'backend_port_info/pg_rpc_port'))
        Global.BackendConfig.monitor_rpc_port = int(find_element(port_info, 'backend_port_info/monitor_rpc_port'))
        Global.BackendConfig.log_rpc_port = int(find_element(port_info, 'backend_port_info/log_rpc_port'))
        Global.BackendConfig.inband_rpc_port = int(find_element(port_info, 'backend_port_info/inband_rpc_port'))
        Global.BackendConfig.pppc_rpc_port = int(find_element(port_info, 'backend_port_info/pppc_rpc_port'))
        Global.BackendConfig.log_listen_port = int(find_element(port_info, 'log_port_info/log_listen_port'))

        ###################################################################
        if os.path.exists(Config.USER_PATH):
            try:
                with open(Config.USER_PATH) as f:
                    Global.Users = json.load(f)
            except:
                raise Exception('\nconfig/backend/user.json format error!')
        Global.Users[Global.BackendConfig.engineer] = {
            'password': Global.BackendConfig.engineer_passwd,
            'authority': 3
        }
        if Global.BackendConfig.senior:
            Global.Users[Global.BackendConfig.senior] = {
                'password': Global.BackendConfig.senior_passwd,
                'authority': 2
            }


def find_element(element, path, enable_empty=False):
    """Get XML element's content."""
    if element.find(path) is None:
        raise Exception('\nbackend.xml error, key {0} not found!'.format(path))
    if not enable_empty and not element.find(path).text:
        raise Exception('\nbackend.xml error, key {0} is empty!'.format(path))

    return element.find(path).text
