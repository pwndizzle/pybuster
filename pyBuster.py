#! /usr/bin/python

import sys
import struct
import time
import datetime
import socket
import requests
import re
if sys.version[0] == '2':
    from Queue import Queue
else:
    from queue import Queue
from threading import Thread
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Setup args
parser = argparse.ArgumentParser(description='pyBuster a multi-target URL bruteforcer',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-u','--host', help='Single host to scan')
parser.add_argument('-ul','--hostlist', help='File containing multiple hosts to scan')
parser.add_argument('-w','--wordlist', help='File containing words/paths to test', required=True)
parser.add_argument('-p','--ports', help='Comma separated list of ports to scan', default='80,443')
parser.add_argument('-c','--codes', help='Success HTTP codes comma separated', default='200')
parser.add_argument('-r','--redirect', help='Follow redirects', default=False)
parser.add_argument('-th','--hostthreads', help='Number of concurrent hosts', default=10)
parser.add_argument('-tw','--wordthreads', help='Number of threads per host', default=3)
parser.add_argument('-v','--verbose', help='Show more information', action='count')
args = vars(parser.parse_args())


def convert_cidr(cidr):
    (ip, mask) = cidr.split('/')
    mask = int(mask)
    host_bits = 32 - mask
    i = struct.unpack('>I', socket.inet_aton(ip))[0] # note the endianness
    start = (i >> host_bits) << host_bits # clear the host bits
    end = (start | ((1 << host_bits) - 1))+1

    ip_list = []
    for i in range(start, end):
        ip_list.append(socket.inet_ntoa(struct.pack('>I',i)))
    return ip_list

# Load hosts and words
try:
    temp_host_list = []
    host_list = []

    if args["host"]:
        temp_host_list.append(args["host"])
    elif args["hostlist"]:
        with open(args["hostlist"]) as file:
            temp_host_list = file.read().strip().split('\n')

    for t in temp_host_list:
        if "/" in t:
            for ip in convert_cidr(t):
                host_list.append(ip)
        else:
            host_list.append(t)

    path_list = []
    with open(args["wordlist"]) as file:
        path_list = file.read().strip().split('\n')
    print (datetime.datetime.now())
    print ("[*] Hosts: " + str(len(host_list)) )
    print ("[*] Paths: " + str(len(path_list)) )
except IOError:
    print ("[!] Error: Coudn't read input file")
    sys.exit(1)

# Parse additional args
ports = [int(x) for x in args["ports"].split(",")]
codes = [int(x) for x in args["codes"].split(",")]
redirect = bool(args["redirect"])
host_threads = int(args["hostthreads"])
word_threads = int(args["wordthreads"])
verbose = args["verbose"]

# Check if port is open
def check_port(host,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        status = s.connect_ex((host, port))
        s.close()
        if status == 0:
            if verbose: print ("[*] Port open: " + str(host) + " - " + str(port))
            return check_path(host,port,"test")
        else:
            if verbose: print ("[!] Error: Cannot reach " + str(host))
            return 0
    except socket.error:
        if verbose: print ("[!] Error: Cannot reach " + str(host))
        return 0
        
    

# Check if path exists
def check_path(host,port,path):
    try:
        url = str(host) + ":" + str(port) + '/' + str(path)
        if "443" in str(port):
            url = 'https://' + str(url)
        else:
            url = 'http://' + str(url)

        response = requests.get(url, verify=False, timeout=2, allow_redirects=redirect)

        if response.status_code in codes:
            title = re.search('(?<=<title>).+?(?=</title>)', response.text, re.DOTALL)
            if title:
                title = title.group().strip()
            else:
                title = ""
            print (str(response.status_code) + "," + str(len(response.content)) + "," + url + "," + title)
        elif verbose:
            print (str(response.status_code) + "," + str(len(response.content)) + "," + url)
        return 1

    except Exception as e:
        if verbose: print ("[!] Error: Timeout or unexpected response from " + str(host) + ":" + str(port) + '/' + str(path) )
        return 0

# Query a single path
def path_worker(host,port,pathq):
    while pathq.qsize():
        path = pathq.get()
        check_path(host,port,path)
        pathq.task_done()


# Create threads for each host
def host_worker(hostq):

    while hostq.qsize():
        host = hostq.get()
        open_ports = []
        for port in ports:
            if check_port(host,port):
                open_ports.append(port)

        for port in open_ports:

            pathq = Queue()

            for path in path_list:
                pathq.put(path)

            for i in range(word_threads):
                t = Thread(target=path_worker,args=(host,port,pathq))
                t.daemon = True
                t.start()

            pathq.join()
        
        if verbose: print ("[*] Host complete: " + str(host) + ":" + str(port))

        hostq.task_done()
        

def main():

    try:
        hostq = Queue()
        threads = []
        
        for host in host_list:
            hostq.put(host)
        
        for i in range(host_threads):
             t = Thread(target=host_worker,args=(hostq,))
             t.daemon = True
             t.start()
             threads.append(t)

        while True:
            print ("Complete: " + str(len(host_list) - hostq.qsize()) + "/" + str(len(host_list)))
            i = 0
            if all(t.isAlive() == False for t in threads):
                break
            time.sleep(3)
        
    except (KeyboardInterrupt, SystemExit):
        print ('\n[!] Stopping scan.\n')


main()
