# -*- coding: utf-8 -*-

"""
backend.pppserv_ice
~~~~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import sys
import Ice
import json

from ..globals import Global

Ice.loadSlice('./backend/lib/pppserv.ice')
import vMseppp


def send(request):
    ic, reply = None, None
    port = Global.BackendConfig.pppserv_rpc_port

    try:
        ic = Ice.initialize(sys.argv)
        base = ic.stringToProxy('SimpleppprpcIf:default -h 127.0.0.1 -p {0}'.format(port))
        communicator = vMseppp.ppprpcifPrx.checkedCast(base)
        if not communicator:
            raise RuntimeError('Invalid proxy')
        reply = communicator.ppprpcproc(request)
    except:
        pass

    if ic:
        try:
            ic.destroy()
        except:
            pass
    
    return reply