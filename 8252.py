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
#import visa
import fakevisa as visa
import signal
import argparse


def measure_current(savename=None, volt=8, step=1, hold=10, mode=2):
    Time = time.time()
    stop = Time + hold  # figure out when to stop

    rm = visa.ResourceManager()
    inst = rm.open_resource('GPIB0::1::INSTR')
    inst.write('Z\n')  # reset unit
    inst.write('SOV+%d\n' % volt)  # set voltage
    inst.write('F%d\n' % mode)  # F2 = Current, F1 = Voltage, F3 = Resistance, F4 = Cap
    inst.write('OPR\n')  # Operate
    data = []
    i = 0
    while time.time() < stop:
        timer = float(hold - (time.time() - Time))
        out = inst.read()
        data.append([timer, float(out[3:])])
        print(data[i], 'sec, A')
        # add user break ability
        # https://stackoverflow.com/questions/20576960/python-infinite-while-loop-break-on-user-input

        signal.signal(signal.SIGALRM, alarmHandler)
        signal.alarm(step)
        try:
            # maybe better to do it this way...
            # https://stackoverflow.com/questions/13207678/whats-the-simplest-way-of-detecting-keyboard-input-in-python-from-the-terminal
            text = raw_input("Type q/Q + return to quit and save:")
            signal.alarm(0)  # disable the alarm
            if "q" in text or "Q" in text:
                print("Breaking")
                break
        except AlarmException:
            signal.signal(signal.SIGALRM, signal.SIG_IGN)

        i += 1
    inst.write('SBY\n')  # Standby

    if savename:
        with open(savename+'.csv', 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(data)
    print('Done')


class AlarmException(Exception):
    pass


def alarmHandler(signum, frame):
    raise AlarmException

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Apply DC field and measure'
            ' quantities with ADCMT 8252 electrometer')
    # best to use string and not argparse.FileType
    # https://stackoverflow.com/questions/18862836/how-to-open-file-using-argparse
    parser.add_argument('-f', '--savename', type=str,
                        help='.csv file to save data in',
                        default=None)
    parser.add_argument('-v', '--volt', type=float,
                        help='DC voltage to apply',
                        default=8.0)
    parser.add_argument('-s', '--step', type=int,
                        help='time [sec] between measurement steps',
                        default=1)
    parser.add_argument('-t', '--hold', type=float,
                        help='Total application time [sec]',
                        default=10.0)
    parser.add_argument("-m", "--mode", type=int, choices=[1, 2, 3, 4],
                        help="1=Voltage, 2=Current, 3=Resistance,4=Capacitance",
                        default=2)

    args = parser.parse_args()

    if args.savename:
        if not os.path.exists(args.savename) :
            print("Already a file.\nUse diffrent name.")
            sys.exit
    measure_current(args.savename, args.volt, args.step, args.hold, args.mode)
