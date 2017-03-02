# -*- coding: utf-8 -*-

"""
backend.log_ice
~~~~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import sys
import Ice
import json

from ..globals import Global

Ice.loadSlice('./backend/lib/log.ice')
import GNLogMgr


def send(request):
    ic, reply = None, None
    port = Global.BackendConfig.log_rpc_port

    try:
        ic = Ice.initialize(sys.argv)
        base = ic.stringToProxy('SimpleGNLogIf:default -h 127.0.0.1 -p {0}'.format(port))
        communicator = GNLogMgr.GNLogRPCIfPrx.checkedCast(base)
        if not communicator:
            raise RuntimeError('Invalid proxy')
        reply = communicator.GetLog(request)
    except:
        pass

    if ic:
        try:
            ic.destroy()
        except:
            pass
    
    return reply