# -*- coding: utf-8 -*-

"""
backend.restful
~~~~~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import json
try:
    from flask import Flask, jsonify, request
except ImportError:
    raise Exception('flask not installed. (try pip install flask)')

from . import user
from . import subinterface
from . import system
from .globals import Global
from .utils import (get_type_id_seq, add_username_ip_port,
    ice_exception_return_data, is_timeout)
from .ice import (inband_ice, log_ice, monitor_ice, pg_ice, pm_ice,
    pppc_ice, pppserv_ice, sm_ice, tm_ice)


app = Flask(__name__)


###########################################################################
@app.route('/vmse/localweb/backend/login/json/', methods=['POST'])
def login():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    if msg_type == 4097:      # log in
        return user.login(req)
    elif msg_type == 4112:    # log out
        return user.logout(req)


@app.route('/vmse/localweb/backend/adminconf/json/', methods=['POST'])
@app.route('/vmse/localweb/backend/sysconf/json/', methods=['POST'])
def backend_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    if msg_type == 4107:      # change authority
        return user.change_authority(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    if msg_type == 4099:      # add user
        return user.add_user(req)
    elif msg_type == 4148:    # reboot
        return system.reboot(req)
    elif msg_type == 4101:    # modify_user
        return user.modify_user(req)
    elif msg_type == 4103:    # delete_user
        return user.delete_user(req)
    # elif msg_type == 4119:    # export key
    #     pass
    # elif msg_type == 4121:    # import license
    #     pass
    # elif msg_type == 4123:    # delete all users
    #     return user.delete_all_users(req)
    elif msg_type == 4146:    # set system time
        return system.set_system_time(req)
    elif msg_type == 4156:    # export config 
        return system.export_config(req)
    elif msg_type == 4158:    # import config
        return system.import_config(req)
    # elif msg_type == 4160:    # import config finsih
    #     pass
    # elif msg_type == 4164:    # update by url, not used
    #     pass
    elif msg_type == 4168:    # set system name
        return system.set_device_name(req)
    # elif msg_type == 4172:    # set access mode, not used
    #     pass


@app.route('/vmse/localweb/backend/getinfo/json/', methods=['POST'])
def backend_getinfo():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq)
    if ret:
        return ret

    if msg_type == 4105:      # get all users
        return user.get_all_users(req)
    elif msg_type == 4115:    # get current session mode
        return system.get_current_session_mode(req)
    # elif msg_type == 4117:    # show license info
    #     pass
    elif msg_type == 4144:    # get system time
        return system.get_system_time(req)
    elif msg_type == 4154:    # get system info
        return system.get_system_info(req)
    # elif msg_type == 4166:    # 查询升级进度
    #     pass
    elif msg_type == 4170:    # get device name
        return system.get_device_name(req)
    # elif msg_type == 4174:    # get access mode
    #     pass


###########################################################################
@app.route('/vmse/localweb/monitor/getinfo/json/', methods=['POST'])
@app.route('/vmse/localweb/mn_sysinfo/getinfo/json/', methods=['POST'])
@app.route('/vmse/localweb/mn_procinfo/getinfo/json/', methods=['POST'])
def monitor_getinfo():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq)
    if ret:
        return ret

    try:
        return jsonify(eval(monitor_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


@app.route('/vmse/localweb/monitor/adminconf/json/', methods=['POST'])
def monitor_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    try:
        return jsonify(eval(monitor_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


###########################################################################
@app.route('/vmse/localweb/ppp_config/getinfo/json/', methods=['POST'])
def ppp_getinfo():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq)
    if ret:
        return ret

    try:
        return jsonify(eval(pppserv_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


@app.route('/vmse/localweb/ppp_config/adminconf/json/', methods=['POST'])
def ppp_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    try:
        return jsonify(eval(pppserv_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


###########################################################################
@app.route('/vmse/localweb/tm_config/getinfo/json/', methods=['POST'])
def tm_getinfo():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq)
    if ret:
        return ret

    try:
        return jsonify(eval(tm_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


@app.route('/vmse/localweb/tm_config/adminconf/json/', methods=['POST'])
def tm_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    try:
        return_data = eval(tm_ice.send(json.dumps(add_username_ip_port(req))))
    except:
        return jsonify(ice_exception_return_data(req))

    if msg_type == 12500:
        subinterface.change_subinterface_status(req['tm_config'].get('admin_status'),
                                                req['tm_config'].get('vlink'))
    if msg_type == 12502:
        subinterface.change_all_subinterface_status(req['tm_config'].get('linktype'),
                                                    req['tm_config'].get('action_type'))

    return jsonify(return_data)


###########################################################################
@app.route('/vmse/localweb/tm_config-pm_sysconf-inband/adminconf/json/', methods=['POST'])
def tm_pm_inband_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    if msg_type == 12311:
        return subinterface.add_inner_subinterface(req)
    elif msg_type == 12313:
        return subinterface.delete_inner_subinterface(req)
    elif msg_type == 12315:
        return subinterface.modify_inner_subinterface(req)
    elif msg_type == 12379:
        return subinterface.delete_all_inner_subinterface(req)
    elif msg_type == 12373:
        return subinterface.add_subinterface_group(req)
    elif msg_type == 12375:
        return subinterface.modify_subinterface_group(req)
    elif msg_type == 12377:
        return subinterface.delete_subinterface_group(req)
    elif msg_type == 12387:
        return subinterface.delete_all_subinterface_group(req)


@app.route('/vmse/localweb/tm_config-inband/adminconf/json/', methods=['POST'])
def tm_inabnd_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    if msg_type == 12311:
        return subinterface.add_outer_subinterface(req)
    elif msg_type == 12313:
        return subinterface.delete_outer_subinterface(req)
    elif msg_type == 12315:
        return subinterface.modify_outer_subinterface(req)
    elif msg_type == 12391:
        return subinterface.delete_all_outer_subinterface(req)


###########################################################################
@app.route('/vmse/localweb/inband/getinfo/json/', methods=['POST'])
def inband_getinfo():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq)
    if ret:
        return ret

    try:
        return jsonify(eval(inband_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


@app.route('/vmse/localweb/inband/adminconf/json/', methods=['POST'])
def inband_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    try:
        return jsonify(eval(inband_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


###########################################################################
@app.route('/vmse/localweb/sm_sysconf/getinfo/json/', methods=['POST'])
@app.route('/vmse/localweb/sm_config/getinfo/json/', methods=['POST'])
def sm_getinfo():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq)
    if ret:
        return ret

    try:
        return jsonify(eval(sm_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


@app.route('/vmse/localweb/sm_config/adminconf/json/', methods=['POST'])
@app.route('/vmse/localweb/sm_sysconf/adminconf/json/', methods=['POST'])
def sm_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    try:
        return jsonify(eval(sm_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


###########################################################################
@app.route('/vmse/localweb/pm_config/getinfo/json/', methods=['POST'])
@app.route('/vmse/localweb/pm_config/getconf/json/', methods=['POST'])
@app.route('/vmse/localweb/pm_sysconf/getinfo/json/', methods=['POST'])
def pm_getinfo():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq)
    if ret:
        return ret

    try:
        return jsonify(eval(pm_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


@app.route('/vmse/localweb/pm_config/adminconf/json/', methods=['POST'])
def pm_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    try:
        return jsonify(eval(pm_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


###########################################################################
@app.route('/vmse/localweb/pm_sysconf-ppp_config-inband/adminconf/json/', methods=['POST'])
def pm_ppp_inabnd_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    return subinterface.synchronous_access_mode(req)


###########################################################################
@app.route('/vmse/localweb/log/getinfo/json/', methods=['POST'])
def log_getinfo():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq)
    if ret:
        return ret

    try:
        return jsonify(eval(log_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


@app.route('/vmse/localweb/log/adminconf/json/', methods=['POST'])
def log_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    try:
        return jsonify(eval(log_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


###########################################################################
@app.route('/vmse/localweb/radius/getinfo/json/', methods=['POST'])
def radius_getinfo():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq)
    if ret:
        return ret

    try:
        return jsonify(eval(pg_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


@app.route('/vmse/localweb/radius/adminconf/json/', methods=['POST'])
def radius_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    try:
        return jsonify(eval(pg_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


###########################################################################
@app.route('/vmse/webportal/sm_sysconf/userlogin/json/', methods=['POST'])
def web_protal():
    req = request.get_json(force=True)

    # Web protal don't need to judge authority and session
    try:
        return jsonify(eval(sm_ice.send(json.dumps(req))))
    except:
        return jsonify(ice_exception_return_data(req))


###########################################################################
@app.route('/vmse/localweb/ha_config/getinfo/json/', methods=['POST'])
def ha_getinfo():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq)
    if ret:
        return ret

    try:
        return jsonify(eval(ha_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


@app.route('/vmse/localweb/ha_config/adminconf/json/', methods=['POST'])
def ha_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    try:
        return jsonify(eval(ha_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


###########################################################################
@app.route('/vmse/localweb/pc_config/getinfo/json/', methods=['POST'])
def pc_getinfo():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq)
    if ret:
        return ret

    try:
        return jsonify(eval(pppc_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


@app.route('/vmse/localweb/pc_config/adminconf/json/', methods=['POST'])
def pc_adminconf():
    req = request.get_json(force=True)
    msg_type, client_id, msg_seq = get_type_id_seq(req)

    ret = is_timeout(client_id, msg_seq, authority='config')
    if ret:
        return ret

    try:
        return jsonify(eval(pppc_ice.send(json.dumps(add_username_ip_port(req)))))
    except:
        return jsonify(ice_exception_return_data(req))


@app.before_request
def before():
    if Global.BackendConfig.print_enable == 1 and Global.BackendConfig.print_level == 7:
        print('Request:\n{0}'.format(request.get_data()))


@app.after_request
def after(response):
    if Global.BackendConfig.print_enable == 1 and Global.BackendConfig.print_level == 7:
        print('Reply:\n{0}'.format(response.response[0]))

    return response