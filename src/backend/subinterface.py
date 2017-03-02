# -*- coding: utf-8 -*-

"""
backend.subinterface
~~~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import json
from flask import jsonify
import xml.etree.ElementTree

from .config import Config
from .ice import tm_ice, pm_ice, inband_ice, pppserv_ice
from .utils import get_type_id_seq, parse_share_xml, write_share_xml, debug


def get_rollback_data(vlink_pairs):
    vlink_info = list()
    for vlink_pair in vlink_pairs:
        data = {
            'linktype': vlink_pair.find('linktype').text,
            'access_type': vlink_pair.find('access_type').text if vlink_pair.find('access_type').text else '',
            'aliasname': vlink_pair.find('aliasname').text,
            'gatewayip': vlink_pair.find('gatewayip').text if vlink_pair.find('gatewayip').text else '0.0.0.0',
            'innervlan': vlink_pair.find('innervlan').text if vlink_pair.find('innervlan').text else '',
            'ipaddr': vlink_pair.find('ipaddr').text if vlink_pair.find('ipaddr').text else '',
            'linkpri': vlink_pair.find('linkpri').text if vlink_pair.find('linkpri').text else '',
            'maxrate': vlink_pair.find('maxrate').text if vlink_pair.find('maxrate').text else '',
            'netmask': vlink_pair.find('netmask').text if vlink_pair.find('netmask').text else '',
            'outervlan': vlink_pair.find('outervlan').text if vlink_pair.find('outervlan').text else '',
            'phyname': vlink_pair.find('phyname').text if vlink_pair.find('phyname').text else '',
            'linkweight': vlink_pair.find('linkweight').text if vlink_pair.find('linkweight').text else '',
            'admin_status': vlink_pair.find('admin_status').text,
        }
        if int(vlink_pair.find('linktype')) == 1:
            data['natpool'] = vlink_pair.find('pool').text if vlink_pair.find('pool').text else ''
        if int(vlink_pair.find('linktype')) == 3:
            data['dhcppool'] = vlink_pair.find('pool').text if vlink_pair.find('pool').text else ''
        vlink_info.append(data)

    return vlink_info


def synchronous_access_mode(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    # 获取回滚的数据
    rollback_aaa_info = list()
    access_mode = vlink.find('access_mode')
    if access_mode is None:
        vlink.append(xml.etree.ElementTree.fromstring('<access_mode></access_mode>'))
        access_mode = vlink.find('access_mode')
    for aaa_pair in access_mode.findall('aaa_pair'):
        rollback_aaa_info.append({
            'type': aaa_pair.find('type').text,
            'interface': aaa_pair.find('interface').text
        })

    rollback_data = {
        'msg_type': 20527,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'AAA_info': rollback_aaa_info
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'confnum': len(req[req.keys()[0]].get('AAA_info')),
        'reply_status': 1
    }

    ret = send_data_to_pm_pppserv_inband(req, return_data, rollback_data)
    if ret:
        return ret

    for aaa_info in req[req.keys()[0]].get('AAA_info'):
        if aaa_info['interface'] in [i.text for i in access_mode.findall('aaa_pair/interface')]:    # modify
            for aaa_pair in access_mode.findall('aaa_pair'):
                if aaa_info['interface'] == aaa_pair.find('interface').text:
                    aaa_pair.find('type').text = aaa_info['type']
        else:    # add
            string = '<aaa_pair><type>{0}</type><interface>{1}</interface></aaa_pair>'.format(
                aaa_info['type'], aaa_info['interface'])
            access_mode.append(xml.etree.ElementTree.fromstring(string))
    write_share_xml(tree)

    return jsonify({'pm_config': return_data})


def add_inner_subinterface(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 12369,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'vlink': get_rollback_data(vlink.findall('vlink_single/vlink_pair'))
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'confnum': str(len(req[req.keys()[0]].get('vlink'))),
        'reply_status': 1
    }

    ret = send_data_to_tm_pm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    vlink_single = vlink.find('vlink_single')
    if vlink_single is None:
        vlink.append(xml.etree.ElementTree.fromstring('<vlink_single></vlink_single>'))
        vlink_single = vlink.find('vlink_single')
    for i in req[req.keys()[0]].get('vlink'):
        vlink_single.append(xml.etree.ElementTree.fromstring(create_inner_subinterface_string(i)))
    write_share_xml(tree)

    return jsonify({'tm_config': return_data})


def modify_inner_subinterface(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 12369,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'vlink': get_rollback_data(vlink.findall('vlink_single/vlink_pair'))
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'confnum': str(len(req[req.keys()[0]].get('vlink'))),
        'reply_status': 1
    }

    ret = send_data_to_tm_pm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    vlink_single = vlink.find('vlink_single')
    for i in req[req.keys()[0]].get('vlink'):
        for vlink_pair in vlink_single.findall('vlink_pair'):
            if i['aliasname'] == vlink_pair.find('aliasname').text:
                vlink_single.remove(vlink_pair)    # modify: delete -> add
                vlink_single.append(xml.etree.ElementTree.fromstring(create_inner_subinterface_string(i)))
    write_share_xml(tree)

    return jsonify({'tm_config': return_data})


def delete_inner_subinterface(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 12369,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'vlink': get_rollback_data(vlink.findall('vlink_single/vlink_pair'))
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'confnum': str(len(req[req.keys()[0]].get('vlink'))),
        'reply_status': 1
    }

    ret = send_data_to_tm_pm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    vlink_single = vlink.find('vlink_single')
    if vlink_single:
        for i in req[req.keys()[0]].get('vlink'):
            for vlink_pair in vlink_single.findall('vlink_pair'):
                if i['aliasname'] == vlink_pair.find('aliasname').text:
                    vlink_single.remove(vlink_pair)
    write_share_xml(tree)

    return jsonify({'tm_config': return_data})
    

def delete_all_inner_subinterface(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 12369,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'vlink': get_rollback_data(vlink.findall('vlink_single/vlink_pair'))
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'reply_status': 1
    }

    ret = send_data_to_tm_pm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    vlink_single = vlink.find('vlink_single')
    if vlink_single:
        for vlink_pair in vlink_single.findall('vlink_pair'):
            if vlink_pair.find('linktype').text == '3':
                vlink_single.remove(vlink_pair)
    write_share_xml(tree)

    return jsonify({'tm_config': return_data})


def add_outer_subinterface(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 12369,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'vlink': get_rollback_data(vlink.findall('vlink_single/vlink_pair'))
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'confnum': str(len(req[req.keys()[0]].get('vlink'))),
        'reply_status': 1
    }

    ret = send_data_to_tm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    vlink_single = vlink.find('vlink_single')
    if vlink_single is None:
        vlink.append(xml.etree.ElementTree.fromstring('<vlink_single></vlink_single>'))
        vlink_single = vlink.find('vlink_single')
    for i in req[req.keys()[0]].get('vlink'):
        vlink_single.append(xml.etree.ElementTree.fromstring(create_outer_interface_string(i)))
    write_share_xml(tree)

    return jsonify({'tm_config': return_data})


def modify_outer_subinterface(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 12369,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'vlink': get_rollback_data(vlink.findall('vlink_single/vlink_pair'))
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'confnum': str(len(req[req.keys()[0]].get('vlink'))),
        'reply_status': 1
    }

    ret = send_data_to_tm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    vlink_single = vlink.find('vlink_single')
    for i in req[req.keys()[0]].get('vlink'):
        for vlink_pair in vlink_single.findall('vlink_pair'):
            if i['aliasname'] == vlink_pair.find('aliasname').text:
                vlink_single.remove(vlink_pair)
                vlink_single.append(xml.etree.ElementTree.fromstring(create_outer_subinterface_string(i)))
    write_share_xml(tree)

    return jsonify({'tm_config': return_data})


def delete_outer_subinterface(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 12369,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'vlink': get_rollback_data(vlink.findall('vlink_single/vlink_pair'))
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'confnum': str(len(req[req.keys()[0]].get('vlink'))),
        'reply_status': 1
    }

    ret = send_data_to_tm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    vlink_single = vlink.find('vlink_single')
    if vlink_single:
        for i in req[req.keys()[0]].get('vlink'):
            for vlink_pair in vlink_single.findall('vlink_pair'):
                if i['aliasname'] == vlink_pair.find('aliasname').text:
                    vlink_single.remove(vlink_pair)
    write_share_xml(tree)

    return jsonify({'tm_config': return_data})
    

def delete_all_outer_subinterface(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 12369,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'vlink': get_rollback_data(vlink.findall('vlink_single/vlink_pair'))
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'reply_status': 1
    }

    ret = send_data_to_tm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    vlink_single = vlink.find('vlink_single')
    if vlink_single:
        for vlink_pair in vlink_single.findall('vlink_pair'):
            if vlink_pair.find('linktype').text in ['1', '2']:
                vlink_single.remove(vlink_pair)
    write_share_xml(tree)

    return jsonify({'tm_config': return_data})


def add_subinterface_group(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 4176,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'rollback': 4
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'reply_status': 1
    }

    ret = send_data_to_tm_pm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    string = ''.join(['<vlink_name>{0}</vlink_name>'.format(req[req.keys()[0]]['vlink_name']),
                     '<phyname>{0}</phyname>'.format(req[req.keys()[0]]['phyname']),
                     '<dhcppool>',
                     '<poolname>{0}</poolname>'.format(req[req.keys()[0]]['dhcppool']['poolname']),
                     '<start_ip>{0}</start_ip>'.format(req[req.keys()[0]]['dhcppool']['start_ip']),
                     '<end_ip>{0}</end_ip>'.format(req[req.keys()[0]]['dhcppool']['end_ip']),
                     '<netmask>{0}</netmask>'.format(req[req.keys()[0]]['dhcppool']['netmask']),
                     '</dhcppool>'])
    for i in req[req.keys()[0]].get('vlan_info'):
        string += '<vlan_info>{0}</vlan_info>'.format(''.join(['<{0}>{1}</{2}>'.format(key, i[key], key) for key in i.keys()]))
    vlink.insert(0, xml.etree.ElementTree.fromstring('<vlink_group>{0}</vlink_group>'.format(string)))
    write_share_xml(tree)

    return jsonify({'pm_config': return_data})


def modify_subinterface_group(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 4176,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'rollback': 4
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'reply_status': 1
    }

    ret = send_data_to_tm_pm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    for vlink_group in vlink.findall('vlink_group'):
        if vlink_group.find('vlink_name').text == req[req.keys()[0]]['vlink_name']:
            vlink.remove(vlink_group)    # modify: remove -> add
            string = ''.join(['<vlink_name>{0}</vlink_name>'.format(req[req.keys()[0]]['vlink_name']),
                              '<phyname>{0}</phyname>'.format(req[req.keys()[0]]['phyname']),
                              '<dhcppool>',
                              '<poolname>{0}</poolname>'.format(req[req.keys()[0]]['dhcppool']['poolname']),
                              '<start_ip>{0}</start_ip>'.format(req[req.keys()[0]]['dhcppool']['start_ip']),
                              '<end_ip>{0}</end_ip>'.format(req[req.keys()[0]]['dhcppool']['end_ip']),
                              '<netmask>{0}</netmask>'.format(req[req.keys()[0]]['dhcppool']['netmask']),
                              '</dhcppool>'])
            for i in req[req.keys()[0]].get('vlan_info'):
                string += '<vlan_info>{0}</vlan_info>'.format(''.join(['<{0}>{1}</{2}>'.format(key, i[key], key) for key in i.keys()]))
            vlink.insert(0, xml.etree.ElementTree.fromstring('<vlink_group>{0}</vlink_group>'.format(string)))
    write_share_xml(tree)

    return jsonify({'pm_config': return_data})


def delete_subinterface_group(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 4176,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'rollback': 4
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'reply_status': 1
    }

    ret = send_data_to_tm_pm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    for vlink_group in vlink.findall('vlink_group'):
        for vlink_name in [i['vlink_name'] for i in req[req.keys()[0]]['vlink_group']]:
            if vlink_group.find('vlink_name').text == vlink_name:
                vlink.remove(vlink_group)
    write_share_xml(tree)

    return jsonify({'pm_config': return_data})


def delete_all_subinterface_group(req):
    msg_type, client_id, msg_seq = get_type_id_seq(req)
    tree, root, vlink = parse_share_xml()

    rollback_data = {
        'msg_type': 4176,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'rollback': 4
    }

    return_data = {
        'msg_type': msg_type + 1,
        'client_id': client_id,
        'msg_seq': msg_seq,
        'reply_status': 1
    }

    ret = send_data_to_tm_pm_inband(req, return_data, rollback_data)
    if ret:
        return ret

    for vlink_group in vlink.findall('vlink_group'):
        vlink.remove(vlink_group)
    write_share_xml(tree)

    return jsonify({'pm_config': return_data})


def send_data_to_pm_pppserv_inband(req, return_data, rollback_data):
    try:
        pm_return = eval(pm_ice.send(json.dumps(req)))
        debug('PM return:\n{0}'.format(pm_return))
    except:
        return_data['reply_status'] = 3
        return jsonify({'pm_config': return_data})
    else:
        if pm_return[pm_return.keys()[0]].get('reply_status') != 1:
            debug('PM rollback:\n{0}'.format(str({'pm_config': rollback_data})))
            i = eval(pm_ice.send(json.dumps({'pm_config': rollback_data})))
            debug('PM rollback return:\n{0}'.format(i))
            return jsonify(pm_return)

    try:
        pppserv_return = eval(pppserv_ice.send(json.dumps(req)))
        debug('PPPServ return:\n{0}'.format(pppserv_return))
    except:
        debug('PM rollback:\n{0}'.format(str({'pm_config': rollback_data})))
        i = eval(pm_ice.send(json.dumps({'pm_config': rollback_data})))
        debug('PM rollback return:\n{0}'.format(i))
        return_data['reply_status'] = 3
        return jsonify({'pm_config': rollback_data})
    else:
        if pppserv_return[pppserv_return.keys()[0]].get('reply_status') != 1:
            debug('PM and PPPServ rollback:\n{0}'.format(str({'pm_config': rollback_data})))
            i = eval(pm_ice.send(json.dumps({'pm_config': rollback_data})))
            j = eval(pppserv_ice.send(json.dumps({'pm_config': rollback_data})))
            debug('PM rollback return:\n{0}'.format(i))
            debug('PPPServ rollback return:\n{0}'.format(j))
            return jsonify(pppserv_return)

    try:
        inband_return = eval(inband_ice.send(json.dumps(req)))
        debug('Inband return:\n{0}'.format(inband_return))
    except:
        debug('PM and PPPServ rollback:\n{0}'.format(str({'pm_config': rollback_data})))
        i = eval(pm_ice.send(json.dumps({'pm_config': rollback_data})))
        j = eval(pppserv_ice.send(json.dumps({'pm_config': rollback_data})))
        debug('PM rollback return:\n{0}'.format(i))
        debug('PPPServ rollback return:\n{0}'.format(j))
        return_data['reply_status'] = 3
        return jsonify({'pm_config': rollback_data})
    else:
        if inband_return[inband_return.keys()[0]].get('reply_status') != 1:
            debug('PM, PPPServ and Inband rollback:\n{0}'.format(str({'pm_config': rollback_data})))
            i = eval(pm_ice.send(json.dumps({'pm_config': rollback_data})))
            j = eval(pppserv_ice.send(json.dumps({'pm_config': rollback_data})))
            k = eval(inband_ice.send(json.dumps({'pm_config': rollback_data})))
            debug('PM rollback return:\n{0}'.format(i))
            debug('PPPServ rollback return:\n{0}'.format(j))
            debug('Inband rollback return:\n{0}'.format(k))
            return jsonify(inband_return)


def send_data_to_tm_pm_inband(req, return_data, rollback_data):    # deal inner vlink and vlink group
    try:
        tm_return = eval(tm_ice.send(json.dumps(req)))
        debug('TM return:\n{0}'.format(tm_return))
    except:    # ice transport exception
        return_data['reply_status'] = 3
        return jsonify({'tm_config': return_data})
    else:
        if tm_return[tm_return.keys()[0]].get('reply_status') != 1:
            debug('TM rollback:\n{0}'.pormat(str({'tm_config': rollback_data})))
            i = eval(tm_ice.send(json.dumps({'tm_config': rollback_data})))
            debug('TM rollback return:\n{0}'.format(i))
            return jsonify(tm_return)

    try:
        pm_return = eval(pm_ice.send(json.dumps(req)))
        debug('PM return:\n{0}'.format(pm_return))
    except:
        debug('TM rollback:\n{0}'.pormat(str({'tm_config': rollback_data})))
        i = eval(tm_ice.send(json.dumps({'tm_config': rollback_data})))
        debug('TM rollback return:\n{0}'.format(i))
        return_data['reply_status'] = 3
        return jsonify({'tm_config': return_data})
    else:
        if pm_return[pm_return.keys()[0]].get('reply_status') != 1:
            debug('TM and PM rollback:\n{0}'.pormat(str({'tm_config': rollback_data})))
            i = eval(tm_ice.send(json.dumps({'tm_config': rollback_data})))
            j = eval(pm_ice.send(json.dumps({'tm_config': rollback_data})))
            debug('TM rollback return:\n{0}'.format(i))
            debug('PM rollback return:\n{0}'.format(j))
            return jsonify(pm_return)

    try:
        inband_return = eval(inband_ice.send(json.dumps(req)))
        debug('Inband return:\n{0}'.format(inband_return))
    except:
        debug('TM and PM rollback:\n{0}'.pormat(str({'tm_config': rollback_data})))
        i = eval(tm_ice.send(json.dumps({'tm_config': rollback_data})))
        j = eval(pm_ice.send(json.dumps({'tm_config': rollback_data})))
        debug('TM rollback return:\n{0}'.format(i))
        debug('PM rollback return:\n{0}'.format(j))
        return_data['reply_status'] = 3
        return jsonify({'tm_config': return_data})
    else:
        if inband_return[inband_return.keys()[0]].get('reply_status') != 1:
            debug('TM, PM and Inband rollback:\n{0}'.pormat(str({'tm_config': rollback_data})))
            i = eval(tm_ice.send(json.dumps({'tm_config': rollback_data})))
            j = eval(pm_ice.send(json.dumps({'tm_config': rollback_data})))
            k = eval(inband_ice.send(json.dumps({'tm_config': rollback_data})))
            debug('TM rollback return:\n{0}'.format(i))
            debug('PM rollback return:\n{0}'.format(j))
            debug('Inband rollback return:\n{0}'.format(k))
            return jsonify(inband_return)


def send_data_to_tm_inband(req, return_data, rollback_data):    # deal outer vlink
    try:
        tm_return = eval(tm_ice.send(json.dumps(req)))
        debug('TM return:\n{0}'.format(tm_return))
    except:    # ice transport exception
        return_data['reply_status'] = 3
        return jsonify({'tm_config': return_data})
    else:
        if tm_return[tm_return.keys()[0]].get('reply_status') != 1:
            debug('TM rollback:\n{0}'.format(str({'tm_config': rollback_data})))
            i = eval(tm_ice.send(json.dumps({'tm_config': rollback_data})))
            debug('TM rollback return:\n{0}'.format(i))
            return jsonify(tm_return)

    try:
        inband_return = eval(inband_ice.send(json.dumps(req)))
        debug('Inband return:\n{0}'.format(inband_return))
    except:
        debug('TM rollback:\n{0}'.format(str({'tm_config': rollback_data})))
        i = eval(tm_ice.send(json.dumps({'tm_config': rollback_data})))
        debug('TM rollback return:\n{0}'.format(i))
        return_data['reply_status'] = 3
        return jsonify({'tm_config': return_data})
    else:
        if inband_return[inband_return.keys()[0]].get('reply_status') != 1:
            debug('TM and Inband rollback:\n{0}'.format(str({'tm_config': rollback_data})))
            i = eval(tm_ice.send(json.dumps({'tm_config': rollback_data})))
            j = eval(inband_ice.send(json.dumps({'tm_config': rollback_data})))
            debug('TM rollback return:\n{0}'.format(i))
            debug('Inband rollback return:\n{0}'.format(j))
            return jsonify({'tm_config': inband_return})


def change_subinterface_status(admin_status, vlink_list):
    tree, root, vlink = parse_share_xml()
    for i in vlink_list:
        for vlink_pair in vlink.findall('vlink_single/vlink_pair'):
            if vlink_pair.find('aliasname').text == i['aliasname']:
                vlink_pair.find('admin_status').text = str(admin_status)
    write_share_xml(tree)


def change_all_subinterface_status(linktype, action_type):
    tree, root, vlink = parse_share_xml()
    if linktype == 0:    # inner subinterface
        for vlink_pair in vlink.findall('vlink_single/vlink_pair'):
            if vlink_pair.find('linktype').text == '3':
                if action_type == 0:    # inactive all
                    vlink_pair.find('admin_status').text = '0'
                elif action_type == 1:   # active all
                    vlink_pair.find('admin_status').text = '1'
    elif linktype == 1:    # outer subinterface
        for vlink_pair in vlink.findall('vlink_single/vlink_pair'):
            if vlink_pair.find('aliasname').text in ['1', '2']:
                if action_type == 0:    # inactive all
                    vlink_pair.find('admin_status').text = '0'
                elif action_type == 1:   # active all
                    vlink_pair.find('admin_status').text = '1'


def create_inner_subinterface_string(i):
    return ''.join(['<vlink_pair>'
                    '<aliasname>{0}</aliasname>'.format(i.get('aliasname', '')),
                    '<access_type>{0}</access_type>'.format(i.get('access_type', '')),
                    '<outervlan>{0}</outervlan>'.format(i.get('outervlan', '')),
                    '<innervlan>{0}</innervlan>'.format(i.get('innervlan', '')),
                    '<ipaddr>{0}</ipaddr>'.format(i.get('ipaddr', '')),
                    '<netmask>{0}</netmask>'.format(i.get('netmask', '')),
                    '<phyname>{0}</phyname>'.format(i.get('phyname', '')),
                    '<gatewayip>{0}</gatewayip>'.format(i.get('gatewayip', '')),
                    '<maxrate>{0}</maxrate>'.format(i.get('maxrate', '')),
                    '<linkweight>{0}</linkweight>'.format(i.get('linkweight', '')),
                    '<linkpri>{0}</linkpri>'.format(i.get('linkpri', '')),
                    '<linktype>{0}</linktype>'.format(i.get('linktype', '')),
                    '<pool>{0}</pool>'.format(i.get('dhcppool', '')),
                    '<admin_status>{0}</admin_status>'.format(i.get('admin_status', '')),
                    '<backup_vlink></backup_vlink>',
                    '</vlink_pair>'])


def create_outer_subinterface_string(i):
    if i['linktype'] == 1:
        return ''.join(['<vlink_pair>'
                        '<aliasname>{0}</aliasname>'.format(i.get('aliasname', '')),
                        '<access_type>{0}</access_type>'.format(i.get('access_type', '')),
                        '<outervlan>{0}</outervlan>'.format(i.get('outervlan', '')),
                        '<innervlan>{0}</innervlan>'.format(i.get('innervlan', '')),
                        '<ipaddr>{0}</ipaddr>'.format(i.get('ipaddr', '')),
                        '<netmask>{0}</netmask>'.format(i.get('netmask', '')),
                        '<phyname>{0}</phyname>'.format(i.get('phyname', '')),
                        '<gatewayip>{0}</gatewayip>'.format(i.get('gatewayip', '')),
                        '<maxrate>{0}</maxrate>'.format(i.get('maxrate', '')),
                        '<linkweight>{0}</linkweight>'.format(i.get('linkweight', '')),
                        '<linkpri>{0}</linkpri>'.format(i.get('linkpri', '')),
                        '<linktype>{0}</linktype>'.format(i.get('linktype', '')),
                        '<pool>{0}</pool>'.format(i.get('natpool', '')),
                        '<admin_status>{0}</admin_status>'.format(i.get('admin_status', '')),
                        '<backup_vlink></backup_vlink>',
                        '</vlink_pair>'])
    elif i['linktype'] == 2:
        return ''.join(['<vlink_pair>'
                        '<aliasname>{0}</aliasname>'.format(i.get('aliasname', '')),
                        '<access_type>{0}</access_type>'.format(i.get('access_type', '')),
                        '<outervlan>{0}</outervlan>'.format(i.get('outervlan', '')),
                        '<innervlan>{0}</innervlan>'.format(i.get('innervlan', '')),
                        '<ipaddr>{0}</ipaddr>'.format(i.get('ipaddr', '')),
                        '<netmask>{0}</netmask>'.format(i.get('netmask', '')),
                        '<phyname>{0}</phyname>'.format(i.get('phyname', '')),
                        '<gatewayip>{0}</gatewayip>'.format(i.get('gatewayip', '')),
                        '<maxrate>{0}</maxrate>'.format(i.get('maxrate', '')),
                        '<linkweight>{0}</linkweight>'.format(i.get('linkweight', '')),
                        '<linkpri>{0}</linkpri>'.format(i.get('linkpri', '')),
                        '<linktype>{0}</linktype>'.format(i.get('linktype', '')),
                        '<pool></pool>',
                        '<admin_status>{0}</admin_status>'.format(i.get('admin_status', '')),
                        '<backup_vlink></backup_vlink>',
                        '</vlink_pair>'])