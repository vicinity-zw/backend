# -*- coding: utf-8 -*-

"""
backend.pppc_ice
~~~~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import sys
import Ice
import json

from ..globals import Global

Ice.loadSlice('./backend/lib/pppc.ice')
import vMsePC


def send(request):
    ic, reply = None, None
    port = Global.BackendConfig.pppc_rpc_port

    try:
        ic = Ice.initialize(sys.argv)
        base = ic.stringToProxy('SimplePCIf:default -h 127.0.0.1 -p {0}'.format(port))
        communicator = vMsePC.PCIfPrx.checkedCast(base)
        if not communicator:
            raise RuntimeError('Invalid proxy')
        reply = communicator.PCrpc(request)
    except:
        pass

    if ic:
        try:
            ic.destroy()
        except:
            pass
    
    return reply