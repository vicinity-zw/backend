# -*- coding: utf-8 -*-

"""
backend.heartbeat
~~~~~~~~~~~~~~~~~

This is the heartbeat server of backend.

:copyright: (c) 2016 by AgileNet.
"""
import socket
import threading

from .globals import Global


class Heartbeat(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.host = '127.0.0.1'
        self.port = Global.BackendConfig.heartbeat_port

    def run(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            raise Exception('\nCan not create TCP socket.')

        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server.bind((self.host, self.port))
        except socket.error:
            raise Exception('\nCan not bind to port {0}'.format(self.port))

        server.listen(2)

        while True:
            client, _ = server.accept()

            try:
                while True:
                    if client.recv(20) == 'heartbeat':
                        client.sendall(''.join(['00', str(Global.BackendConfig.pid)]))
                    else:
                        break
            finally:
                client.close()