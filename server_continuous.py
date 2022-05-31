#!/usr/bin/env python3
import argparse
import os
import pwd
import socket
import struct
import sys
import threading
import time
import traceback
import signal
from datetime import datetime
from datetime import timedelta

print("continuous")

PATH = '/tmp/aloha.socket'
SLOT = 0.1
parser = argparse.ArgumentParser()
parser.add_argument('--path', default=PATH)
parser.add_argument('--slot', type=float, default=SLOT)
args = parser.parse_args()

close = False
clients = set()
failedclients = set()
clients_lock = threading.Lock()
sleep_schedule = []
timer_started = False

def signal_handler(sig, frame):
    os._exit(0)
signal.signal(signal.SIGINT, signal_handler)

def Handler(client_sock, result):
    try:
        with client_sock:
            if result:
                client_info = client_sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize('3i'))
                client_pid, client_uid, client_gid = struct.unpack('3i', client_info)
                #print('Accept {}'.format(pwd.getpwuid(client_uid).pw_gecos.split(',')[0].split(' ')[-1]))
                client_sock.sendall(b'0x01')
            else:
                client_sock.sendall(b'0x00')
    except:
        pass
    finally:
        with clients_lock:
            clients.remove(client_sock)
            if client_sock in failedclients:
                failedclients.remove(client_sock)

def Timer():
    global sleep_schedule
    while not close:
        while (len(sleep_schedule) == 0):
            time.sleep(args.slot/2)
            
        if (sleep_schedule[0][0]-datetime.today()).total_seconds()>0:
            time.sleep((sleep_schedule[0][0]-datetime.today()).total_seconds())
        
        with clients_lock:
            #for client_sock in clients:
            threading.Thread(target=Handler, args=(sleep_schedule[0][1], len(clients)==1 and sleep_schedule[0][1] not in failedclients)).start()
            #clients.clear()
            if (len(sleep_schedule) > 1):
                for cl in clients:
                    failedclients.add(cl)
                sleep_schedule = sleep_schedule[1:]
            else:
                sleep_schedule = []


try:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server_sock:
        try:
            os.unlink(args.path)
        except:
            pass
        server_sock.bind(args.path)
        os.chmod(args.path, 0o777)
        server_sock.listen(1)
        while True:
            client_sock, _ = server_sock.accept()
            sleep_schedule.append((datetime.now()+timedelta(seconds=args.slot), client_sock))

            if not timer_started:
                threading.Thread(target=Timer).start()
                timer_started = True
            with clients_lock:
                clients.add( client_sock )
except:
    traceback.print_exc()
    close = True
