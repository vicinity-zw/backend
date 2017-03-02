# -*- coding: utf-8 -*-

"""
backend.cli
~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import os
import gevent
import gevent.queue, gevent.server
from telnetserver import TelnetHandlerBase, command

from .config import Config
from .globals import Global


class TelnetHandler(TelnetHandlerBase):
    def __init__(self, request, client_address, server):
        self.cookedq = gevent.queue.Queue()
        TelnetHandlerBase.__init__(self, request, client_address, server)

    def setup(self):
        TelnetHandlerBase.setup(self)
        self.greenlet_ic = gevent.spawn(self.inputcooker)
        gevent.sleep(0.5)

    def finish(self):
        TelnetHandlerBase.finish(self)
        self.greenlet_ic.kill()

    def getc(self, block=True):
        try:
            return self.cookedq.get(block)
        except gevent.queue.Empty:
            return ''

    def inputcooker_socket_ready(self):
        return gevent.select.select([self.sock.fileno()], [], [], 0) != ([], [], [])

    def inputcooker_store_queue(self, char):
        if type(char) in [type(()), type([]), type("")]:
            for v in char:
                self.cookedq.put(v)
        else:
            self.cookedq.put(char)


class MyTelnetHandler(TelnetHandler):
    PROMPT = 'Backend> '
    WELCOME = "Welcome to backend."
    authNeedPass = True

    COMMAND_LIST = [
        ('help', 'Show help info.'),
        ('history', 'Show command history.'),
        ('show log_enable', 'Show log_enable info.'),
        ('show log_level', 'Show log_level info.'),
        ('show printf_enable', 'Show printf_enable info.'),
        ('show printf_level', 'Show printf_level info.'),
        ('show session', 'Show online sessions.')]

    def authCallback(self, username, password):
        if password != Config.TELNET_PASSWORD:
            raise

    def showHelp(self):
        return '\n'.join(['{0:<20} {1}'.format(l[0], l[1]) for l in self.COMMAND_LIST]) + '\n\n'

    def getCommonString(self, line, line_list):
        line_list = sorted(line_list, key=len)
        for i in range(len(line) + 1, len(line_list[0]) + 1):
            for j in line_list:
                if j.startswith(line_list[0][:i]):
                    continue
                else:
                    return line_list[0][:i - 1]

    def tabAutoComplete(self, line, insptr):
        line = filter(lambda x: x != '\t', line)
        if line == []:
            return ''
        else:
            line_list = []
            for command in [l[0] for l in self.COMMAND_LIST]:
                if command[:len(line)] == ''.join(line):
                    line_list.append(command)
            if line_list == []:
                return ''
            elif len(line_list) == 1:
                return line_list[0][len(line):]
            else:
                common_str = self.getCommonString(''.join(line), line_list)
                return common_str[len(line):]

    @command('show')
    def command_show(self, params):
        if params == ['log_enable']:
            self.writeresponse(show_log_enable())
        elif params == ['log_level']:
            self.writeresponse(show_log_level())
        elif params == ['printf_enable']:
            self.writeresponse(show_printf_enable())
        elif params == ['printf_level']:
            self.writeresponse(show_printf_level())
        elif params == ['session']:
            self.writeresponse(show_session())
        else:
            self.writeresponse('Unknow command %s' % ' '.join(params))

def show_log_enable():
    return ' log_enable: {0}\n'.format(Global.BackendConfig.log_enable)

def show_log_level():
    return ' log_level: {0}\n'.format(Global.BackendConfig.log_level)

def show_printf_enable():
    return ' printf_enable: {0}\n'.format(Global.BackendConfig.print_enable)

def show_printf_level():
    return ' printf_level: {0}\n'.format(Global.BackendConfig.print_level)

def show_session():
    '''name ip port last_operate_time'''
    return ''


def init_cli():
    server = gevent.server.StreamServer(('', globals.TELNET_PORT), MyTelnetHandler.streamserver_handle)
    server.serve_forever()