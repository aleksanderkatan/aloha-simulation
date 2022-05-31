#!/usr/bin/env python3
import argparse
import socket
import time
import random
import signal
import os
from datetime import datetime
from datetime import timedelta


PATH = '/tmp/aloha.socket'
SLOT = 0.1
CHANCE = 1
MULT = 2
parser = argparse.ArgumentParser()
parser.add_argument('--path', default=PATH)
parser.add_argument('--slot', type=float, default=SLOT)
parser.add_argument('--packet-probability', type=float, default=CHANCE)
parser.add_argument('--first-interval', type=float, default=SLOT)
parser.add_argument('--multiplier', type=float, default=MULT)
parser.add_argument('--name', type=str, default="client")
args = parser.parse_args()

totalwaittime = 0.0
denies = 0
accepts = 0
totalsent = 0
waittime = 0

def signal_handler(sig, frame):
    f = open("temp/data." + args.name, "w")
    f.write(str(totalwaittime) + " " + str(denies) + " " + str(accepts) + " " + str(totalsent))
    f.close()
    os._exit(0)
signal.signal(signal.SIGINT, signal_handler)

try:
    while True:
        if waittime > 0:
            tm = random.random()*waittime
            totalwaittime += tm 
            time.sleep(tm)
        else:
            if (random.random() >= args.packet_probability):
                time.sleep(args.slot)
                continue

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_sock:
            client_sock.connect(args.path)
            totalsent+=1
            data = client_sock.recv(1024)
            if data == b'0x01':
                #print('Accepted')
                waittime = 0
                accepts+=1
            else:
                #print('Failed')
                if waittime == 0:
                    waittime = args.first_interval
                else:
                   waittime *= args.multiplier
                denies +=1
    
except Exception:
    pass

#f = open("temp/data." + args.name, "w")
#f.write(str(totalwaittime) + "\n" + str(denies) + "\n" + str(accepts) + "\n" + str(totalsent))
#f.close()