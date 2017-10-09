# 8252-electrometer
Controller for ADCMT 8252 electrometer using NI GPIB-USB-HS and visa

For Python 2.7 with visa


# 8252.py
is a comand line controller.
usage: 8252.py [-h] [-f SAVENAME] [-v VOLT] [-s STEP] [-t HOLD] [-m {1,2,3,4}]

Apply DC field and measure quantities with ADCMT 8252 electrometer

optional arguments:
  -h, --help            show this help message and exit
  -f SAVENAME, --savename SAVENAME
                        .csv file to save data in
  -v VOLT, --volt VOLT  DC voltage to apply
  -s STEP, --step STEP  time [sec] between measurement steps
  -t HOLD, --hold HOLD  Total application time [sec]
  -m {1,2,3,4}, --mode {1,2,3,4}
                        1=Voltage, 2=Current, 3=Resistance,4=Capacitance

# gui_8252.py and controll_8252.py
Run controll_8252.py to start gui'ed application version that includes live plotting

### Requires:
pyqt-4
matplotlib
