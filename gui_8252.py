# -*- coding: utf-8 -*-
"""GUI for ADCMT 8252 electrometer using NI GPIB-USB-HS and visa"""
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

from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# ####################################################
# Try Encoding (Error prevention)
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
# ####################################################

# Set Up Fonts
# Normal font
font_N = QtGui.QFont()
font_N.setFamily(_fromUtf8("Georgia"))
font_N.setPointSize(14)
# Lable Font
font_L = QtGui.QFont()
font_L.setFamily(_fromUtf8("Georgia"))
font_L.setPointSize(18)
# Bold Font
font_B = QtGui.QFont()
font_B.setFamily(_fromUtf8("Georgia"))
font_B.setPointSize(18)
# Title Font
font_T = QtGui.QFont()
font_T.setFamily(_fromUtf8("Georgia"))
font_T.setPointSize(24)

QtGui.QToolTip.setFont(QtGui.QFont('Georgia', 12))  # set the font

# Set up Styles
ButtonStyle = "QPushButton{ \
        background: qlineargradient(x1 : 0, y1 : 0, x2 : 0, y2 :1, stop : 0.0 lightgrey, stop : 1 white ); \
        padding: 6px; \
        border-style: outset; \
        border-width: 1px; border-color: grey; } \
        QPushButton:pressed { \
        background: qlineargradient(x1 : 0, y1 : 0, x2 : 0, y2 : 1, stop : 0.0 grey, stop : 1 lightgrey ); }"
ButtonStopStyle = "QPushButton{ \
        background: qlineargradient(x1 : 0, y1 : 0, x2 : 0, y2 : 1, stop : 0.0 hsv(0, 255, 210), stop : 1 hsv(0, 255, 255) ); \
        padding: 6px; \
        border-style: outset; \
        border-width: 1px; \
        border-color: grey; } \
        QPushButton:pressed { \
        background: qlineargradient(x1 : 0, y1 : 0, x2 : 0, y2 : 1, stop : 0.0 hsv(0, 255, 160), stop : 1 hsv(0, 255, 210) ); }"
# style for lcd display boxes
styl = "Background-color: transparent; color: black; border-style: ridge; border-width: 1px; border-color: grey;"

# #####################################################
# Setup Main Window


class gui(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        # could also use 'super(gui, self).__init__()' calls the parent class

        self.setupUi(self)  # make the UI  See Bellow

    def setupUi(self, MainWindow):

        # System Checks.  Avoid errors!!
        if sys.platform == "darwin":  # check if you are on a mac
            QtGui.qt_mac_set_native_menubar(False)   # disable native menues

        # Set Up Widget(Form)
        # set up size policy (Currently no using a size policy
        # but left the below in incase I decide to add it)
        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
        #                                QtGui.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())

    # Setup Main Window
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        # MainWindow.setMaximumSize(100,100) #height, width
        # MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setWindowTitle("8252 Electrometer Controller")

        # central widget (widget "gui" of the main window)
        self.centralwidget = QtGui.QWidget(MainWindow)
        # self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
# bring in other class widgets (See below for classes)
        self.stack = StackedWidget()
        self.Test = Test()
        self.Terminal = Terminal()

# ##############

# ##############
# Set up buttion actions and changes (Button Click is defined below)
        self.Test.Button.clicked.connect(lambda: self.ButtonClick())

# ###############
# Setup Main Layout

    # Set up stack (this allows for the switching between pages)
        self.stack.addWidget(self.Test)
        self.stack.addWidget(self.Terminal)

    # create vertical layout
        self.layoutV = QtGui.QVBoxLayout(self.centralwidget)
        self.layoutV.addWidget(self.stack)      # stack of pages
    # add to main window to display
        MainWindow.setCentralWidget(self.centralwidget)

# Add program Status Bar at bottom
        self.statusbar = QtGui.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.statusbar.showMessage(_fromUtf8("Program On"))

# Menu Bar
    # Set up Menu items
        self.page0 = QtGui.QAction(QtGui.QIcon('img/Test.png'),
                                   '  Time', self)  # set up the action
        self.page0.triggered.connect(lambda: self.stack.setPage(0))
        self.page0.setShortcut('Ctrl+1')    # give it a shortcut

        self.page1 = QtGui.QAction(QtGui.QIcon('img/Terminal.png'),
                                   '  Terminal', self)  # set up the action
        self.page1.triggered.connect(lambda: self.stack.setPage(1))
        self.page1.setShortcut('Ctrl+2')    # give it a shortcut

    # Add the Menu Bar
        self.menu = self.menuBar()
        self.fileMenu = self.menu.addMenu('&Mode')
        # Add Items
        self.fileMenu.addAction(self.page0)
        self.fileMenu.addAction(self.page1)
# ######################
# function to change button from a start to a stop (change styl and text)
    def ButtonClick(self):
        # what button sent the command??
        sending_button = self.sender()
        name = sending_button.objectName()
        self.ChangeButton(name)

    def ChangeButton(self, name, chk=""):
        # what button sent the command??
        sending_button = self.findChild(QtGui.QPushButton, name)
        text = sending_button.text()
        # Was it a start button?
        if text[0:5] == "Start" and chk != "Stop":    # Start button to Stop
            text = "Stop!%s" % text[5:]
            sending_button.setText(text)
            sending_button.setStyleSheet(ButtonStopStyle)
        elif text[0:5] == "Stop!":  # Stop button to Start
            text = "Start%s" % text[5:]
            sending_button.setText(text)
            sending_button.setStyleSheet(ButtonStyle)

        elif text[-4:] == "Stop":   # Setup Stop  button
            text = text[0:-5]
            sending_button.setText(text)
            sending_button.setStyleSheet(ButtonStyle)
        elif chk != "Stop":                       # Setup start Button
            text = "%s Stop" % text
            sending_button.setText(text)
            sending_button.setStyleSheet(ButtonStopStyle)


# ####################################################
# ####################################################
# Setup Basic Gui Page (could be inherited by others (Lowers amount of code))
class Test(QtGui.QWidget):
    def __init__(self):
        super(Test, self).__init__()
        self.setupUi()  # make the UI  See Bellow
        self.initUi()

    def setupUi(self):
        # Setup Title
        self.Title = QtGui.QLabel()
        self.Title.setFont(font_T)
        self.Title.setAlignment(QtCore.Qt.AlignCenter)
        # Voltage input
        self.volt = QtGui.QSpinBox()
        # self.val.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.volt.setRange(0, 100)
        self.volt.setSingleStep(5)
        self.volt.setValue(10)

        self.Label1 = QtGui.QLabel()
        self.Label1.setText(_fromUtf8("Voltage [V]:"))
        self.volt.setToolTip(_fromUtf8('Please input an integer between 0 and 100'))
        self.Label1.setFont(font_L)

    # Measure
        self.combo = QtGui.QComboBox(self)
        self.combo.addItem("Voltage")
        self.combo.addItem("Current")
        self.combo.addItem("Resistance")
        self.combo.addItem("Capacitance")
        self.combo.setCurrentIndex(1)

        self.comboLabel = QtGui.QLabel()
        self.comboLabel.setText(_fromUtf8("Measure:"))
        self.comboLabel.setFont(font_L)

        # Step time
        self.step = QtGui.QSpinBox()
        self.step.setRange(0, 10000)
        self.step.setSingleStep(100)
        self.step.setValue(1000)
        # self.hz.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.Label2 = QtGui.QLabel()
        self.Label2.setText(_fromUtf8("Step Time [msec]:"))
        self.step.setToolTip(_fromUtf8('Please input an integer between 0 and 10,000'))
        self.Label2.setFont(font_L)

        # Hold Time
        self.hold = QtGui.QSpinBox()
        self.hold.setRange(0, 1800)
        self.hold.setSingleStep(30)
        self.hold.setValue(60)
        # self.hz.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.Label3 = QtGui.QLabel()
        self.Label3.setText(_fromUtf8("Time [sec]:"))
        self.hold.setToolTip(_fromUtf8('Please input an integer between 0 and 1800'))
        self.Label3.setFont(font_L)

        # Save Name
        self.name = QtGui.QLineEdit(self)
        # self.name.move(80, 20)
        # self.e.resize(200, 32)
        # self.nameLabel.move(20, 20)

        self.Label4 = QtGui.QLabel(self)
        self.Label4.setText('Save Name:')
        self.name.setToolTip(_fromUtf8('Data is automatically saved as a .csv'))
        self.Label4.setFont(font_L)

    # Name Button
        self.nameButton = QtGui.QPushButton(_fromUtf8("..."))
        self.nameButton.resize(60, 40)
        self.nameButton.setFont(font_B)
        self.nameButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.nameButton.setStyleSheet(ButtonStyle)
        self.nameButton.setObjectName(_fromUtf8("nameB"))

    # Button
        self.Button = QtGui.QPushButton(_fromUtf8("Start"))
        self.Button.resize(100, 60)
        self.Button.setFont(font_B)
        self.Button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Button.setStyleSheet(ButtonStyle)

        self.Button.setObjectName(_fromUtf8("Test"))

        self.volt.setObjectName("volt")
        self.step.setObjectName("step")
        self.hold.setObjectName("hold")
        self.name.setObjectName("name")
        self.combo.setObjectName("combo")

    # Plot Canvas
        # a figure instance to plot on
        self.figure = Figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot(111)

    def initUi(self):
        # set up grid layout
        self.vbox = QtGui.QVBoxLayout()
        self.voltbox = QtGui.QHBoxLayout()
        self.combobox = QtGui.QHBoxLayout()
        self.stepbox = QtGui.QHBoxLayout()
        self.holdbox = QtGui.QHBoxLayout()
        self.namebox = QtGui.QHBoxLayout()
        self.plotbox = QtGui.QVBoxLayout()
        self.hbox = QtGui.QHBoxLayout()
        # add Layouts

        self.voltbox.addWidget(self.Label1)
        self.voltbox.addWidget(self.volt)
        self.combobox.addWidget(self.comboLabel)
        self.combobox.addWidget(self.combo)
        self.stepbox.addWidget(self.Label2)
        self.stepbox.addWidget(self.step)
        self.holdbox.addWidget(self.Label3)
        self.holdbox.addWidget(self.hold)
        self.namebox.addWidget(self.Label4)
        self.namebox.addWidget(self.name)
        self.namebox.addWidget(self.nameButton)

        self.plotbox.addWidget(self.toolbar)
        self.plotbox.addWidget(self.canvas)

        self.vbox.addLayout(self.voltbox)
        self.vbox.addLayout(self.combobox)
        self.vbox.addLayout(self.stepbox)
        self.vbox.addLayout(self.holdbox)
        self.vbox.addLayout(self.namebox)
        self.vbox.addWidget(self.Button)
        self.hbox.addLayout(self.vbox)
        self.hbox.addLayout(self.plotbox)
    # Finish Page Setup
        self.setLayout(self.hbox)

        self.nameButton.clicked.connect(self.selectFile)

    def selectFile(self):
        self.name.setText(get_samename(self))


# ####################################################
# Setup Setup Terminal Page
class Terminal(QtGui.QWidget):  # inherit from basic class above
    def __init__(self):
        super(Terminal, self).__init__()
        self.setupUi()  # make the UI  See Bellow
        self.initUi()

    def setupUi(self):
        # Setup Title
        self.Title = QtGui.QLabel()
        self.Title.setFont(font_T)
        self.Title.setText(_fromUtf8("Control Terminal"))
        self.Title.setAlignment(QtCore.Qt.AlignCenter)
        # input
        self.inpt = QtGui.QTextEdit()
        self.inpt.setFont(font_N)
        self.inpt.setMaximumHeight(30)
        self.inptlb = QtGui.QLabel()
        self.inptlb.setFont(font_L)
        self.inptlb.setText(_fromUtf8("Input:"))
        self.inptlb.setAlignment(QtCore.Qt.AlignCenter)
        self.inpt.setToolTip(_fromUtf8('Check manuals for commands. \
            <br> Only send command (return is atomated).'))
        # Button
        self.send = QtGui.QPushButton("Send Command")
        # self.send.resize(10, 60)
        self.send.setFont(font_B)
        self.send.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.send.setStyleSheet(ButtonStyle)
        # Clear History Button
        self.hist_clear = QtGui.QPushButton("Clear History")
        # self.send.resize(100, 60)
        self.hist_clear.setFont(font_B)
        self.hist_clear.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.hist_clear.setStyleSheet(ButtonStyle)

        # history text box
        self.hist = QtGui.QTextEdit()
        self.hist.setReadOnly(True)
        self.hist.setFont(font_N)
        self.histlb = QtGui.QLabel()
        self.histlb.setFont(font_L)
        self.histlb.setText(_fromUtf8("Sent and Recieved Codes:"))
        self.histlb.setAlignment(QtCore.Qt.AlignCenter)

    def initUi(self):
        # set up grid layout
        self.vbox = QtGui.QVBoxLayout()
        self.vbox1 = QtGui.QVBoxLayout()
        self.vbox2 = QtGui.QVBoxLayout()
        self.hbox1 = QtGui.QHBoxLayout()
        self.hbox = QtGui.QHBoxLayout()
        # add Layouts
        self.vbox1.addWidget(self.inptlb)
        self.vbox1.addWidget(self.inpt)
        self.vbox1.addWidget(self.send)
        self.vbox1.addWidget(self.hist_clear)
        self.vbox2.addWidget(self.histlb)
        self.vbox2.addWidget(self.hist)
        self.hbox.addLayout(self.vbox1)
        self.hbox.addLayout(self.vbox2)
        self.vbox.addWidget(self.Title)
        self.vbox.addLayout(self.hbox)
    # Finish Page Setup
        self.setLayout(self.vbox)


# ####################################################
# Setup for fading between 'stacked' widgets.
# (advanced and totally extra - not really needed but fun
# - I could comment/explain if wanted)
class FaderWidget(QtGui.QWidget):

    def __init__(self, old_widget, new_widget):
        # print old_widget, new_widget #for debug
        QtGui.QWidget.__init__(self, new_widget)

        self.old_pixmap = QtGui.QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.0

        self.timeline = QtCore.QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(333)
        self.timeline.start()

        self.resize(new_widget.size())
        self.show()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()

    def animate(self, value):
        self.pixmap_opacity = 1.0 - value
        self.repaint()


class StackedWidget(QtGui.QStackedWidget):

    def __init__(self, parent=None):
        QtGui.QStackedWidget.__init__(self, parent)

    def setCurrentIndex(self, index):
        self.fader_widget = FaderWidget(self.currentWidget(),
                                        self.widget(index))
        QtGui.QStackedWidget.setCurrentIndex(self, index)

    def setPage(self, index=0):
        self.setCurrentIndex(index)


def get_samename(self):
    """Qt file dialogue widget
    """
    filetypes = 'comma seperated values (*.csv)'
    default = QtCore.QDir.homePath()
    fn = QtGui.QFileDialog.getSaveFileName(
                    self,
                    'Save File',
                    default,
                    '*.csv',
                    '*.csv',
                    QtGui.QFileDialog.DontUseNativeDialog)
    if fn:
        fn = str(fn).split(".")[0] + '.csv'
    return fn

# ############################################
# # Start up the Gui
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ex = gui()
    ex.show()
    sys.exit(app.exec_())
