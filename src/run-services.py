#!/usr/bin/env python

import os
from subprocess import Popen

rest = Popen(["python", "rest.py"])
processing = Popen(["python", "processing.py"])

try:
    rest.wait()
    processing.wait()
except KeyboardInterrupt:
    rest.kill()
    processing.kill()
