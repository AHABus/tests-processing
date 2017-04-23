#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
from copy import deepcopy
import re
import sys

UP_REG = r'G\/(B|U|R|D),P([0-9A-F]+)\/([B|U|R|D]),P([0-9A-F]+)\/([B|U|R|D])'
RX_REG = r'\[(\d+)\]: rx stats: (\d+) received, (\d+)\/(\d+) frame bytes \((\d+) fixed\)'

start = None

uptime = {
    'total': 0,
    'gnss': {
        'U': 0,
        'D': 0,
        'R': 0,
    },
    '0A': {
        'U': 0,
        'D': 0,
        'R': 0,
    },
    '14': {
        'U': 0,
        'D': 0,
        'R': 0,
    },
}

stats = {
    'total': 0,
    'valid': 0,
    'invalid': 0,
    'fixed': 0,
    'fixed rate': 0.0,
    'error rate': 0.0,
    'bandwidth': 14
}

history = []

def uprate(i):
    total = i['U'] + i['R'] + i['D']
    if total == 0: return 0
    return i['U'] / total

def export_uptime(path):
    with open(path, "w") as f:
        print("device, up, down, recovering, uprate", file=f)
        print("gnss, %d, %d, %d, %f" % (
        uptime['gnss']['U'], uptime['gnss']['D'], uptime['gnss']['R'], uprate(uptime['gnss'])
        ), file=f)
        print("payload 10, %d, %d, %d, %f" % (
        uptime['0A']['U'], uptime['0A']['D'], uptime['0A']['R'], uprate(uptime['0A'])
        ), file=f)
        print("payload 20, %d, %d, %d, %f" % (
        uptime['14']['U'], uptime['14']['D'], uptime['14']['R'], uprate(uptime['14'])
        ), file=f)

def export_stats(path):
    with open(path, "w") as f:
        print("MET, received, valid, invalid, fixed, error rate, fixed rate, bandwidth", file=f)
        for item in history:
            print("%d, %d, %d, %d, %d, %f, %f, %f" % item, file=f)
        

def parse_system(line):
    #print(line)
    m = re.search(UP_REG, line, re.M|re.I)
    if m:
        uptime['total'] += 1
        uptime['gnss'][m.group(1)] += 1

        uptime['0A'][m.group(3)] += 1
        uptime['14'][m.group(5)] += 1

def parse_stats(line, alpha):
    m = re.search(RX_REG, line, re.M|re.I)
    if m:
        global start
        t = int(m.group(1))
        if not start:
            start = t
        t = t - start
        
        last = deepcopy(stats)
        dt = t - history[-1][0] if len(history) > 0 else 0
        
        stats['total'] = int(m.group(2))
        stats['valid'] = int(m.group(3))
        stats['invalid'] = int(m.group(4))
        if not dt == 0:
            
            fr = (stats['fixed'] - last['fixed']) / dt
            er = (stats['invalid'] - last['invalid']) / dt
            dr = (stats['total'] - last['total']) / dt
            
            stats['fixed rate'] = (1-alpha) * fr + (alpha) * stats['fixed rate']
            stats['error rate'] = (1-alpha) * er + (alpha) * stats['error rate']
            stats['bandwidth'] = alpha * dr + (1-alpha) * stats['bandwidth']
        else:
            stats['fixed rate'] = 0
            stats['error rate'] = 0
            stats['bandwidth'] = 14
        stats['fixed'] = int(m.group(5))
        history.append((t, stats['total'], stats['valid'], stats['invalid'], stats['fixed'], stats['error rate'], stats['fixed rate'], stats['bandwidth']))


if not len(sys.argv) == 3:
    print('usage: process-log.py log_file alpha')
    sys.exit()

path = sys.argv[1]
alpha = float(sys.argv[2])

with open(path, "r") as f:
    for line in f:
        if line.find("FCORE//SYS_HEALTH") > -1:
            parse_system(line)
        if line.find("rx stats:") > -1:
            parse_stats(line, alpha)
    export_uptime("%s.uptime.csv" % path)
    export_stats("%s.rxstats.csv" % path)