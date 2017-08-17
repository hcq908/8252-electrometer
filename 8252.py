#!/usr/bin/env python
"""Controller for ADCMT 8252 electrometer using NI GPIB-USB-HS and visa"""
# Copyright 2017 Austin Fox
# Program is distributed under the terms of the
# GNU General Public License see ./License for more information.

# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import (
         bytes, dict, int, list, object, range, str,
         ascii, chr, hex, input, next, oct, open,
         pow, round, super,
         filter, map, zip)
# #######################

import sys, os
import numpy as np
from random import randint
import csv
import time
import visa
import signal


def measure_current(voltage=8, steptime=1, duration=10, filename=None):
    Time = time.time()
    stop = Time + duration  # figure out when to stop

    rm = visa.ResourceManager()
    inst = rm.open_resource('GPIB0::1::INSTR')
    inst.write('Z\n')  # reset unit
    inst.write('SOV+%d\n' % voltage)  # set voltage
    inst.write('F2\n')  # F2 = Current, F1 = Voltage, F3 = Resistance, F4 = Cap
    inst.write('OPR\n')  # Operate
    data = []
    i = 0
    while time.time() < stop:
        timer = float(duration - (time.time() - Time))
        out = inst.read()
        data.append([timer, float(out[3:])])
        print(data[i], 'sec, A')
        # add user break ability
        # https://stackoverflow.com/questions/20576960/python-infinite-while-loop-break-on-user-input

        signal.signal(signal.SIGALRM, alarmHandler)
        signal.alarm(steptime)
        try:
            # maybe better to do it this way...
            # https://stackoverflow.com/questions/13207678/whats-the-simplest-way-of-detecting-keyboard-input-in-python-from-the-terminal
            text = raw_input("Type q/Q + return to quit and save:")
            signal.alarm(0)
            if "q" in text or "Q" in text:
                print("Breaking")
                break
        except AlarmException:
            signal.signal(signal.SIGALRM, signal.SIG_IGN)

        i += 1
    inst.write('SBY\n')  # Standby

    if filename:
        with open(filename+'.csv', 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(data)
    print('Done')


class AlarmException(Exception):
    pass


def alarmHandler(signum, frame):
    raise AlarmException


if __name__ == '__main__':
    location = [os.path.expanduser('~'), '_The_Universe', '_Materials_Engr',
                '_Mat_Systems', '_BNT_BKT', '_CSD/', '_Data', 'EAPSI',
                'Insitu/elec']

    sample = b'EAPSI_c020_08_g6-02'
    extra = "VU"
    volts = 8
    hold = 60
    savename = os.path.join(os.path.join(*location),
                            sample+"-"+str(volts)+extra)

    if not os.path.exists(savename + '.csv'):
        measure_current(volts, 1, hold, savename)
    else:
        print("already a file")
