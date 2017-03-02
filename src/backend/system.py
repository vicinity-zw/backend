# -*- coding: utf-8 -*-

"""
backend.system
~~~~~~~~~~~~~~

This module is used to manage vMSE system.

:copyright: (c) 2016 by AgileNet.
"""
import os
import time
from flask import jsonify
from datetime import datetime

try:
    import psutil
except ImportError:
    raise Exception('psutil not installed! (try pip install psutil)')

from .config import Config
from .globals import Global
from .utils import get_type_id_seq, get_hostname, set_hostname


def import_config(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'reply_status': 1
    }

    path = '/'.join(['/var/www/html/vmse/uploads', req['bkend_conf']['path'].split('/')[-1]])
    if not os.path.exists(path):
        return_data['reply_status'] = 3
        return jsonify({'bkend_conf': return_data})
    
    try:
        os.system('tar xvf {0}'.format(path))
        os.system('rm -rf {0}/config'.format(Config.PROGRAM_PATH))
        os.system('mv /var/www/html/vmse/uploads/config {0}'.format(Config.PROGRAM_PATH))
    except:
        return_data['reply_status'] = 3
        return jsonify({'bkend_conf': return_data})

    return jsonify({'bkend_conf': return_data})


def export_config(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'path': None,
        'reply_status': 1
    }

    filename = 'vMse_config_{0}.tar.gz'.format(Global.BackendConfig.version)
    try:
        os.system('tar -zcvf {0} config'.format(filename))
        os.system('mv {0}/{1} /var/www/html/vmse'.format(Config.PROGRAM_PATH, filename))
        return_data['path'] = 'http://{0}:{1}/vmse/{2}'.format(req['bkend_conf']['ip'], req['bkend_conf']['port'], filename)
    except:
        return_data['reply_status'] = 3
        return jsonify({'bkend_conf': return_data})

    return jsonify({'bkend_conf': return_data})

 
def set_system_time(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'reply_status': 1
    }

    try:
        os.system('date -s {0}'.format(req['bkend_conf']['system']))
        os.system('clock -w')
    except:
        return_data['reply_status'] = 3
        return jsonify({'bkend_conf': return_data})

    return jsonify({'bkend_conf': return_data})


def reboot(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'reply_status': 1
    }

    # Only engineer has right to reboot or shutdown
    if Global.Sessions[client_id]['username'] != Global.BackendConfig.engineer:
        return_data['reply_status'] = 5
        return jsonify({'bkend_conf': return_data})

    if int(req['bkend_conf']['shuttype']) == 1:
        os.system('shutdown -h now')
    else:
        os.system('reboot')
        
    return jsonify({'bkend_conf': return_data})


def set_device_name(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    set_hostname(req['bkend_conf']['device_name'])

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'reply_status': 1
    }

    return jsonify({'bkend_conf': return_data})


def get_current_session_mode(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'admin_mode': Global.Sessions[client_id]['mode']
    }

    return jsonify({'bkend_conf': return_data})


def get_system_time(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'systime': datetime.now().strftime('%Y%m%d %H:%M:%S')
    }

    return jsonify({'bkend_conf': return_data})


def get_system_info(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'device_name': get_hostname(),
        'setuptime': datetime.fromtimestamp(int(psutil.boot_time())).strftime('%Y-%m-%d %H:%M:%S'),
        'sys_online_time': int(time.time() - psutil.boot_time()),
        'sysytime': str(datetime.now())[:19],
        'dev_model': Global.BackendConfig.dev_model,
        'sys_ver_info': Global.BackendConfig.version
    }

    return jsonify({'bkend_conf': return_data})


def get_device_name(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'device_name': get_hostname(),
        'reply_status': 1
    }

    return jsonify({'bkend_conf': return_data})