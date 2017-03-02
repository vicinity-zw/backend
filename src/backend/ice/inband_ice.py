# -*- coding: utf-8 -*-

"""
backend.inband_ice
~~~~~~~~~~~~~~

:copyright: (c) 2016 by AgileNet.
"""
import sys
import Ice
import json

from ..globals import Global

Ice.loadSlice('./backend/lib/inband.ice')
import vMseIb


def send(request):
    ic, reply = None, None
    port = Global.BackendConfig.inband_rpc_port

    try:
        ic = Ice.initialize(sys.argv)
        base = ic.stringToProxy('SimpleibIf:default -h 127.0.0.1 -p {0}'.format(port))
        communicator = vMseIb.ibIfPrx.checkedCast(base)
        if not communicator:
            raise RuntimeError('Invalid proxy')
        reply = communicator.Ibrpc(request)
    except:
        pass

    if ic:
        try:
            ic.destroy()
        except:
            pass
    
    return reply