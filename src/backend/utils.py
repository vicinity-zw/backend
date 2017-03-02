# -*- coding: utf-8 -*-

"""
backend.utils
~~~~~~~~~~~~~

This module provides utility functions that are used with backend.

:copyright: (c) 2016 by AgileNet.
"""
import os
import time
import json
import subprocess
from flask import jsonify
from copy import deepcopy
import xml.etree.ElementTree

from .config import Config
from .globals import Global


def popen(cmd):
    """Popen with exception handled."""
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if not stderr:
            return stdout
    except:
        pass


def debug(msg):
    """Print debug information. (Only used in vlink.py)"""
    if Global.BackendConfig.print_enable == 1 and Global.BackendConfig.print_level == 7:
        print(msg)


def get_type_id_seq(req):
    """Get msg_type, client_id and msg_seq from request"""
    for i in req:
        if isinstance(req[i], dict):
            return req[i].get('msg_type'), req[i].get('client_id'), req[i].get('msg_seq')


def add_username_ip_port(req):
    """Add username, ip, port to request (use to send operate log)"""
    _, client_id, _ = get_type_id_seq(req)
    req['user_name'] = Global.Sessions[client_id]['username']
    req['ip_port'] = '{0}:{1}'.format(Global.Sessions[client_id]['ip'], Global.Sessions[client_id]['port'])

    return req


def get_hostname():
    with open('/etc/sysconfig/network') as f:
        return [x.split('=')[1] for x in [x for x in f.read().split('\n') if x] if 'HOSTNAME=' in x][0].rstrip()


def set_hostname(hostname):
    with open('/etc/sysconfig/network') as f:
        c = f.read()
    with open('/etc/sysconfig/network', 'w') as f:
        f.write(c.replace([x for x in [x for x in c.split('\n') if x] if 'HOSTNAME=' in x][0], 'HOSTNAME={0}'.format(hostname)))


def ice_exception_return_data(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return {req.keys()[0]:{
            'msg_type': msg_type + 1,
            'client_id': client_id,
            'msg_seq': msg_seq,
            'reply_status': 3
    }}


def save_user():
    d = deepcopy(Global.Users)    
    if Global.BackendConfig.engineer in d:
        d.pop(Global.BackendConfig.engineer)
    if Global.BackendConfig.senior in d:
        d.pop(Global.BackendConfig.senior)

    with open(Config.USER_PATH, 'wb') as f:
        json.dump(d, f, indent=4)


def parse_share_xml():
    tree = xml.etree.ElementTree.parse(Config.SHARE_XML_PATH)
    root = tree.getroot()
    vlink = root.find('vlink')
    if vlink is None:
        root.insert(0, xml.etree.ElementTree.fromstring('<vlink></vlink>'))
        vlink = root.find('vlink')

    return tree, root, vlink


def write_share_xml(tree):
    tree.write(Config.SHARE_XML_PATH)
    os.environ['XMLLINT_INDENT'] = '    '
    os.system('xmllint --format --encode UTF-8 {0} > .tmp'.format(Config.SHARE_XML_PATH))
    os.rename('.tmp', Config.SHARE_XML_PATH)


def is_timeout(client_id, msg_seq, authority=None):
    if client_id not in Global.Sessions:
        return jsonify({'bkend_conf': {
            'msg_type': 4114,
            'client_id': client_id,
            'msg_seq': msg_seq,
            'reply_status': 6    # session time out
        }})

    if time.time() - Global.Sessions[client_id]['last_operate_time'] > Global.BackendConfig.session_lifetime:
        if client_id in Global.Sessions:
            Global.Sessions.pop(client_id)
        return jsonify({'bkend_conf': {
            'msg_type': 4114,
            'client_id': client_id,
            'msg_seq': msg_seq,
            'reply_status': 6    # session time out
        }})

    Global.Sessions[client_id]['last_operate_time'] = time.time()    # update time
    if authority=='config':
        if Global.Users[Global.Sessions[client_id]['username']]['authority'] < 2 and Global.Sessions[client_id]['mode'] != 2:
            return jsonify({'bkend_conf': {
                'msg_type': 4111,
                'client_id': client_id,
                'msg_seq': msg_seq,
                'reply_status': 5
            }})