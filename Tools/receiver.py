#!/usr/local/env python
# -*- coding: utf-8 -*-

import posix_ipc
import time
import json
from datetime import datetime

try :
    mq1 = posix_ipc.MessageQueue("/LinkyRPiQueueGUI", posix_ipc.O_CREAT)
    mq2 = posix_ipc.MessageQueue("/LinkyRPiQueueDB", posix_ipc.O_CREAT)
except :
    print("Error queue")


while True:
    try :
        msg = mq1.receive(timeout = 0)
        trameLue = True
    except :
        trameLue = False

    if trameLue :
        trameDict = dict(json.loads(msg[0]))
        print(" -UI-> " + datetime.now().strftime("%H:%M:%S.%f"))

    try :
        msg = mq2.receive(timeout = 0)
        trameLue = True
    except :
        trameLue = False

    if trameLue :
        trameDict = dict(json.loads(msg[0]))
        print(" -DB-> " + datetime.now().strftime("%H:%M:%S.%f"))
