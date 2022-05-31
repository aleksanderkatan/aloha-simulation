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

print("slotted")

PATH = '/tmp/aloha.socket'
SLOT = 0.1
parser = argparse.ArgumentParser()
parser.add_argument('--path', default=PATH)
parser.add_argument('--slot', type=float, default=SLOT)
args = parser.parse_args()

close = False
clients = list()
clients_lock = threading.Lock()

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

def Timer():
    while not close:
        time.sleep(args.slot)
        with clients_lock:
            for client_sock in clients:
                threading.Thread(target=Handler, args=(client_sock, len(clients)==1)).start()
            clients.clear()
threading.Thread(target=Timer).start()


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
            with clients_lock:
                clients.append( client_sock )
except:
    traceback.print_exc()
    close = True
