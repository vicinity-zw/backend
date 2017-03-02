# -*- coding: utf-8 -*-

"""
backend.user
~~~~~~~~~~~~

This module is used to manage adminstrators of vMSE.

:copyright: (c) 2016 by AgileNet.
"""
import time
from flask import jsonify
import xml.etree.ElementTree

from .config import Config
from .globals import Global
from .utils import get_type_id_seq, save_user


def login(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    username = req['bkend_conf'].get('user_name')
    password = req['bkend_conf'].get('password')

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'user_name': username,
        'admin_mode': 2,
        'reply_status': 1
    }

    if username in Global.Users and Global.Users[username]['password'] == password:
        if len(Global.Sessions) >= Global.BackendConfig.session_hsize:    # Session full
            return_data['reply_status'] = 3
            return jsonify({'bkend_conf': return_data})

        if Global.Users[username]['authority'] == 1:    # 查看权限用户
            return_data['admin_mode'] = 1

            Global.Sessions[client_id] = {
                'username': username,
                'ip': req['bkend_conf']['ipaddr'],
                'port': req['bkend_conf']['tcpport'],
                'mode': return_data['admin_mode'],
                'last_operate_time': time.time()    # last operate time
            }

            return jsonify({'bkend_conf': return_data})
        else:
            if Global.Sessions and 2 in [Global.Sessions[session]['mode'] for session in Global.Sessions]:    # 配置权限用户且有人在配置模式
                return_data['admin_mode'] = 1

                Global.Sessions[client_id] = {
                    'username': username,
                    'ip': req['bkend_conf']['ipaddr'],
                    'port': req['bkend_conf']['tcpport'],
                    'mode': return_data['admin_mode'],
                    'last_operate_time': time.time()    # last operate time
                }

                return jsonify({'bkend_conf': return_data})
            else:
                Global.Sessions[client_id] = {
                    'username': username,
                    'ip': req['bkend_conf']['ipaddr'],
                    'port': req['bkend_conf']['tcpport'],
                    'mode': return_data['admin_mode'],
                    'last_operate_time': time.time()    # last operate time
                }

                return jsonify({'bkend_conf': return_data})
    else:
        return_data['reply_status'] = 4    # Username or password incorrect
        return jsonify({'bkend_conf': return_data})


def logout(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'user_name': req['bkend_conf']['user_name'],
        'reply_status': 1
    }

    if client_id in Global.Sessions:
        Global.Sessions.pop(client_id)    # delete session

    return jsonify({'bkend_conf': return_data})


def add_user(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    username = req['bkend_conf']['user_name']

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'user_name': username,
        'reply_status': 1
    }

    if username in Global.Users:    # username already exists
        return_data['reply_status'] = 12
        return jsonify({'bkend_conf': return_data})
    elif len(Global.Users) >= Global.BackendConfig.user_hsize:    # 用户表已满
        return_data['reply_status'] = 14
        return jsonify({'bkend_conf': return_data})
    else:
        Global.Users[username] = {
            'password': req['bkend_conf']['password'],
            'authority': req['bkend_conf']['admin_pri']
        }
        save_user()
        return jsonify({'bkend_conf': return_data})


def modify_user(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    username = req['bkend_conf']['user_name']
    authority = req['bkend_conf']['admin_pri']

    return_data = {
        'msg_type': msg_seq + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'username': username,
        'reply_status': 1
    }

    if authority == 2:    # Only engineer can change authority to 2
        if Global.Sessions[client_id]['username'] != Global.BackendConfig.engineer:
            return_data['reply_status'] = 5
            return jsonify({'bkend_conf': return_data})

    if username not in Global.Users:    # user not exist
        return_data['reply_status'] = 2
        return jsonify({'bkend_conf': return_data})

    if username == Global.BackendConfig.engineer:
        return_data['reply_status'] = 3
        return jsonify({'bkend_conf': return_data})

    if username == Global.BackendConfig.senior and authority == 1:
        return_data['reply_status'] = 3
        return jsonify({'bkend_conf': return_data})

    password = req['bkend_conf'].get('password')
    if password:
        Global.Users[username]['password'] = password
        Global.Users[username]['authority'] = authority
        save_user()
        if username == Global.BackendConfig.senior:
            tree = xml.etree.ElementTree.parse(Config.CONFIG_FILE_PATH)
            tree.find('senior_passwd').text = password
            tree.write(Config.CONFIG_FILE_PATH)
        return jsonify({'bkend_conf': return_data})
    else:
        Global.Users[username]['authority'] = authority
        save_user()
        return jsonify({'bkend_conf': return_data})


def delete_user(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'conf_num': 0,
        'reply_status': 1
    }

    if 'user_name' in req['bkend_conf']:    # Just delete one user
        username = req['bkend_conf']['user_name']
        if username == Global.BackendConfig.engineer:    # Can not delete engineer
            return_data['reply_status'] = 5
            return jsonify({'bkend_conf': return_data})
        if username == Global.Sessions[client_id]['username']:    # Can not delete himself
            return_data['reply_status'] = 5
            return jsonify({'bkend_conf': return_data})
        if username == Global.BackendConfig.senior:
            if Global.Sessions[client_id]['username'] != Global.BackendConfig.engineer:    # Only engineer can delete senior
                return_data['reply_status'] = 5
                return jsonify({'bkend_conf': return_data})
            else:
                tree = xml.etree.ElementTree.parse(Config.CONFIG_FILE_PATH)
                tree.find('senior').text = ''
                tree.find('senior_passwd').text = ''
                tree.write(Config.CONFIG_FILE_PATH)
                return_data['conf_num'] = 1
                return jsonify({'bkend_conf': return_data})
        Global.Users.pop(username)
        save_user()
        for session in Global.Sessions:
            if Global.Sessions[session]['username'] == username:
                Global.Sessions.pop(session)
        return jsonify({'bkend_conf': return_data})
    elif 'delete_user' in req['bkend_conf']:    # Delete multi users
        user_list = [x['user_name'] for x in req['bkend_conf']['delete_user']]
        if user_list:
            if Global.BackendConfig.engineer in user_list or Global.Sessions[client_id]['username'] in user_list:
                return_data['reply_status'] = 5
                return jsonify({'bkend_conf': return_data})
            if Global.BackendConfig.senior in user_list and Global.Sessions[client_id]['username'] != Global.BackendConfig.engineer:
                return_data['reply_status'] = 5
                return jsonify({'bkend_conf': return_data})
            for username in user_list:
                Global.Users.pop(username)
                [Global.Sessions.pop(x) for x in [x for x in Global.Sessions if Global.Sessions[x]['username'] == username]]
                if username == Global.BackendConfig.senior:
                    tree = xml.etree.ElementTree.parse(Config.CONFIG_FILE_PATH)
                    tree.find('senior').text = ''
                    tree.find('senior_passwd').text = ''
                    tree.write(Config.CONFIG_FILE_PATH)
                    Global.BackendConfig.senior = ''
                    Global.BackendConfig.senior_passwd = ''
            save_user()
            return_data['conf_num'] = len(user_list)
            return jsonify({'bkend_conf': return_data})


def get_all_users(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'list': list(),
        'reply_status': 1
    }

    if req['bkend_conf'].get('user_name'):
        return_data['list'].append({
            'user_id': 1,
            'user_name': req['bkend_conf']['user_name'],
            'admin_pri': Global.Sessions[client_id]['mode']
        })
        return jsonify({'bkend_conf': return_data})
    
    for index, user in enumerate(filter(lambda user: Global.Users[user]['authority'] <= 
        Global.Users[Global.Sessions[client_id]['username']]['authority'], Global.Users)):
        return_data['list'].append({
            'user_id': index + 1,    # index start from 1, not 0
            'user_name': user,
            'admin_pri': Global.Users[user]['authority']
        })
    return jsonify({'bkend_conf': return_data})


def change_authority(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    authority = req['bkend_conf']['admin_mode']

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'admin_mode': authority,
        'reply_status': 1
    }


    if authority == '1':    # 要切换到查看模式
        Global.Sessions[client_id]['mode'] = '1'
        return jsonify({'bkend_conf': return_data})
    else:    # 要切换到配置模式
        if Global.Users[Global.Sessions[client_id]['username']]['authority'] == 1:
            return_data['reply_status'] = 5
            return jsonify({'bkend_conf': return_data})
        elif Global.Sessions[client_id]['username'] == Global.BackendConfig.engineer:    # engineer用户要切换就强制切换
            for session in Global.Sessions:
                Global.Sessions[session]['mode'] = 1
            Global.Sessions[client_id]['mode'] = 2
            return jsonify({'bkend_conf': return_data})
        else:    # 此时需要判断是否强制踢下线
            for session in Global.Sessions:
                if Global.Sessions[session]['username'] == Global.BackendConfig.engineer and Global.Session[session]['mode'] == 2:
                    Global.Sessions[session]['mode'] = 1
                    return_data['reply_status'] = 5
                    return jsonify({'bkend_conf': return_data})

            for session in Global.Sessions:
                Global.Sessions[session]['mode'] = 1
            Global.Sessions[client_id]['mode'] = 2
            return jsonify({'bkend_conf': return_data})