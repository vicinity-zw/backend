# -*- coding: utf-8 -*-

"""
backend.tm_ice
~~~~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import sys
import Ice
import json

from ..globals import Global

Ice.loadSlice('./backend/lib/tm.ice')
import vMsetm


def send(request):
    ic, reply = None, None
    port = Global.BackendConfig.tm_rpc_port

    try:
        ic = Ice.initialize(sys.argv)
        base = ic.stringToProxy('SimpletmIf:default -h 127.0.0.1 -p {0}'.format(port))
        communicator = vMsetm.tmIntfPrx.checkedCast(base)
        if not communicator:
            raise RuntimeError('Invalid proxy')
        reply = communicator.tmrpc(request)
    except:
        pass

    if ic:
        try:
            ic.destroy()
        except:
            pass
    
    return reply