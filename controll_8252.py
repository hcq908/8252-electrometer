#!/usr/bin/env python
"""Controller for ADCMT 8252 electrometer using NI GPIB-USB-HS and visa"""
# Copyright 2017 Austin Fox
# Program is distributed under the terms of the
# GNU General Public License see ./License for more information.

# Python 3 compatibility
# disabled for now b/c of apphistory signal issues
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import (
         bytes, dict, int, list, object, range, str,
         ascii, chr, hex, input, next, oct, open,
         pow, round, super,
         filter, map, zip)
"""
# #######################

import sys, os
import numpy as np
from random import randint
import csv
import time
import signal
from PyQt4 import QtCore, QtGui
#import visa
import fakevisa as visa
import gui_8252


class APP(gui_8252.gui):
    """This Class is used to create the Gui for the laser and
    to controll it."""

    # Creat a python signal that will be used to pass app history stuff
    apphistory = QtCore.pyqtSignal(str)
    stop = float(time.time())
    start = stop

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.init_connection()
        self.running = False
        self.data = []

    def run(self):

        # Set up Button Click and change event refs (Slots)
        self.Test.Button.clicked.connect(lambda: self.testpress())
        # lambda is used to allow you to pass args,  not really needed here...
        self.Terminal.send.clicked.connect(
                lambda: self.send(self.Terminal.inpt.toPlainText()))
        self.Terminal.hist_clear.clicked.connect(self.Terminal.hist.clear)
        # On Value changes update the guiVars dictionary

        self.apphistory.connect(self.Terminal.hist.append)
        self.show()         # show the Gui

    def endisable_all(self):
        if self.Test.volt.isEnabled():
            # print('enabled')
            bol = False
        else:
            bol = True
            # print('disabled')
        self.Test.volt.setEnabled(bol)
        self.Test.combo.setEnabled(bol)
        self.Test.step.setEnabled(bol)
        self.Test.hold.setEnabled(bol)
        self.Test.name.setEnabled(bol)
        self.Test.nameButton.setEnabled(bol)
        self.fileMenu.setEnabled(bol)

    def testpress(self):
        """handle click of the start/stop button"""

        if self.running:
            self.running = False
            return

        if not self.checkname():
            self.ChangeButton("Test")
            return

        volt = self.Test.volt.value()
        combo = self.Test.combo.currentIndex() + 1
        step = self.Test.step.value()
        hold = self.Test.hold.value()

        self.endisable_all()
        self.start_test(volt, step, hold, combo)

# Commands to Run Test

    def init_connection(self):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource('GPIB0::1::INSTR')

    def send(self, cmd):
        self.emit(QtCore.SIGNAL('apphistory(QString)'),
                  time.strftime('%y-%m-%d %H:%M:%S'))
        self.inst.write(cmd + '\n')  # reset unit
        self.emit(QtCore.SIGNAL('apphistory(QString)'),
                  "SEND: %s" % str(cmd).strip())

    def recv(self, debug=False):
        out = self.inst.read()
        if debug:
            self.emit(QtCore.SIGNAL('apphistory(QString)'),
                      "RECV: %s" % str(out).strip())
        return out

    def start_test(self, volt=8, step=1, hold=10, mode=2):
        self.running = True

        self.start = float(time.time())
        self.stop = self.start + hold  # figure out when to stop
        # print('stop', self.stop)

        self.send('Z')
        self.send('SOV+%d' % volt)  # set voltage
        self.send('F%d' % mode)  # F2=Curr, F1=Volt, F3=Resist, F4=Cap
        self.send('OPR')  # Operate
        i = 0
        QtCore.QTimer.singleShot(10, lambda: self.measure(i, step))

    def measure(self, i, step):
        """Loop that retrieves data and refreshes plot"""
        if time.time() > self.stop or not self.running:
            self.end_test()
            return
        timer = float(time.time())
        # print('time', timer)
        out = self.recv()
        self.data.append([timer-self.start, float(out[3:])])
        # print(self.data)
        # discards the old graph
        self.Test.ax.clear()
        # plot data
        arr = np.array(self.data).T
        # print(arr.shape)
        self.Test.ax.plot(arr[0], arr[1], '*-')
        # refresh canvas
        self.Test.canvas.draw()
        i += step
        # print('i', i)
        add = self.start + i/1000
        # print('add', add)
        wait = max(0, add - timer) * 1000
        # print('wait', wait)
        QtCore.QTimer.singleShot(wait, lambda: self.measure(i, step))

    def end_test(self):
        self.running = False
        self.save_data(str(self.Test.name.text()))
        self.data = []  # clear data
        self.send('SBY')  # Standby
        self.endisable_all()
        self.ChangeButton("Test", 'Stop')

    def save_data(self, name):
        if name:
            with open(name, 'wb') as f:
                writer = csv.writer(f)
                writer.writerows(self.data)
        else:
            print("no file name")

    def checkname(self):
        """ Check that filename is good and let user decide what to do"""

        # setup message box
        flags = QtGui.QMessageBox.Yes
        flags |= QtGui.QMessageBox.No
        response = QtGui.QMessageBox.No
        question = 'Error!'
        # test path
        name = str(self.Test.name.text())
        if name:
            if os.path.exists(name):
                question = "Path exist.\nOverwrite data?"
            else:
                return True
        else:
                question = "No Path Specified.\nContinue without saving data?"
        response = QtGui.QMessageBox.question(self, "Bad File Name!",
                                              question,
                                              flags)
        if response == QtGui.QMessageBox.Yes:
            return True
        elif QtGui.QMessageBox.No:
            return False
        else:
            return False


# start it all up
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ex = APP()
    QtCore.QTimer.singleShot(10, ex.run)
    sys.exit(app.exec_())
