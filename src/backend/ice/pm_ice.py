
# -*- coding: utf-8 -*-

"""
backend.pm_ice
~~~~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import sys
import Ice
import json

from ..globals import Global

Ice.loadSlice('./backend/lib/pm.ice')
import vMsePm


def send(request):
    ic, reply = None, None
    port = Global.BackendConfig.pm_rpc_port

    try:
        ic = Ice.initialize(sys.argv)
        base = ic.stringToProxy('SimplePmIf:default -h 127.0.0.1 -p {0}'.format(port))
        communicator = vMsePm.PmIntfPrx.checkedCast(base)
        if not communicator:
            raise RuntimeError('Invalid proxy')
        reply = communicator.pmrpc(request)
    except:
        pass

    if ic:
        try:
            ic.destroy()
        except:
            pass
    
    return reply