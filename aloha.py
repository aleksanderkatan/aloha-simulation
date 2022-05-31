#!/usr/bin/env python3

import sys
import os
import argparse
import time
import signal


SLOT = 0.1
SLOTS = 30
CHANCE = 1
MULT = 2
CLIENTS = 2
FIRST_INTERVAL = 0.5
parser = argparse.ArgumentParser()
parser.add_argument('--slot', type=float, default=SLOT)
parser.add_argument('--slots', type=int, default=SLOTS)
parser.add_argument('--packet-probability', type=float, default=CHANCE)
parser.add_argument('--clients', type=int, default=CLIENTS)
parser.add_argument('--first-interval', type=float, default=FIRST_INTERVAL)
parser.add_argument('--multiplier', type=float, default=MULT)
parser.add_argument('--continuous', action="store_false")
args = parser.parse_args()

if not os.path.exists("./temp"):
    os.makedirs("./temp")

clients = []
server = os.fork()

if not server:
    if args.continuous:
        os.execvp("./server_slotted.py", ["./server_slotted.py", "--slot", str(args.slot)])
    else:
        os.execvp("./server_continuous.py", ["./server_continuous.py", "--slot", str(args.slot)])
    exit(1)

time.sleep(1) #wait for server to be properly set up 

for i in range(args.clients):
    pid = os.fork()
    if not pid:
        os.execvp("./client.py", ["./client.py", "--name", "client"+str(i), "--slot", str(args.slot), "--packet-probability", str(args.packet_probability), "--first-interval", str(args.first_interval), "--multiplier", str(args.multiplier)])
        exit(1)
    else:
        clients.append(pid)


time.sleep(args.slot*args.slots)


for cl in clients:
    os.kill(cl, signal.SIGINT)

os.kill(server, signal.SIGINT)

time.sleep(1)

totalwaittime = 0.0
denies = 0
accepts = 0
totalsent = 0

for i in range(args.clients):
    name = "temp/data.client" + str(i)
    f = open(name, "r")
    data = f.read()
    f.close()
    os.system("rm " + name)
    data = data.split()

    totalwaittime += float(data[0])
    denies += int(data[1])
    accepts += int(data[2])
    totalsent += int(data[3])

print("totalwaittime", totalwaittime)
print("denies", denies)
print("accepts", accepts)
print("totalsent", totalsent)
print()
print("average wait time", totalwaittime/(accepts))
print("packets per slot", accepts/args.slots)


