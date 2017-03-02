# -*- coding: utf-8 -*-

"""
backend.sm_ice
~~~~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import sys
import Ice
import json

from ..globals import Global

Ice.loadSlice('./backend/lib/sm.ice')
import vMseSm


def send(request):
    ic, reply = None, None
    port = Global.BackendConfig.sm_rpc_port

    try:
        ic = Ice.initialize(sys.argv)
        base = ic.stringToProxy('SimplesmIf:default -h 127.0.0.1 -p {0}'.format(port))
        communicator = vMseSm.smIfPrx.checkedCast(base)
        if not communicator:
            raise RuntimeError('Invalid proxy')
        reply = communicator.Smrpc(request)
    except:
        pass

    if ic:
        try:
            ic.destroy()
        except:
            pass
    
    return reply