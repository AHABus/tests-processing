#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
import PIL
import sys
import argparse
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

if not len(sys.argv) == 2:
    print('usage: process-log.py log_file')
    sys.exit()

path = sys.argv[1]

data = np.genfromtxt(path, delimiter=',', names=True)
start_time = data[0][0]

with open(path, "w") as f:
    print("MET, latitude, longitude, altitude", file=f)
    for entry in data:
        print("%d, %d, %d, %d" % (entry[0]-start_time, entry[1], entry[2], entry[3]), file=f)
    f.close()



