#!/usr/local/env python
# -*- coding: utf-8 -*-

#This file is part of LinkyRPi.
#LinkyRPi is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#LinkyRPi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with LinkyRPi. If not, see <https://www.gnu.org/licenses/>.
#(c)Copyright Mikaël Masci 2022


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
