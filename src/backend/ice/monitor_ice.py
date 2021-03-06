# -*- coding: utf-8 -*-

"""
backend.monitor_ice
~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import sys
import Ice
import json

from ..globals import Global

Ice.loadSlice('./backend/lib/monitor.ice')
import vMseMn


def send(request):
    ic, reply = None, None
    port = Global.BackendConfig.monitor_rpc_port

    try:
        ic = Ice.initialize(sys.argv)
        base = ic.stringToProxy('SimplemnIf:default -h 127.0.0.1 -p {0}'.format(port))
        communicator = vMseMn.mnIfPrx.checkedCast(base)
        if not communicator:
            raise RuntimeError('Invalid proxy')
        reply = communicator.Mnrpc(request)
    except:
        pass

    if ic:
        try:
            ic.destroy()
        except:
            pass
    
    return reply