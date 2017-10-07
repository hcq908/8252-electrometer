#!/usr/bin/env python
"""
a visa class emulator
"""
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

import random

class ResourceManager:
    class open_resource:
        def __init__(self, port):
            self.port = port
        def write(self, txt):
            print("fake:", txt)
        def read(self):
            num = random.randint(0, 100)
            return "diq %d" % num
