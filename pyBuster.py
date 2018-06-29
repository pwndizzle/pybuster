#! /usr/bin/python

import sys
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
parser = argparse.ArgumentParser(description='pyBuster a multi-target URL bruteforcer')
parser.add_argument('-u','--hostlist', help='File containing hosts to test', required=True)
parser.add_argument('-w','--wordlist', help='File containing words/paths to test', required=True)
parser.add_argument('-p','--portlist', help='Comma separated list of ports to test', default='80,443')
parser.add_argument('-th','--hostthreads', help='Number of concurrent hosts', default=10)
parser.add_argument('-tw','--wordthreads', help='Number of threads per host', default=3)
parser.add_argument('-v','--verbose', help='Show more information', action='count')
args = vars(parser.parse_args())

# Parse args
host_file = args["hostlist"]
host_list = []
port_list = [int(x) for x in args["portlist"].split(",")]
path_file = args["wordlist"]
path_list = []
host_threads = int(args["hostthreads"])
word_threads = int(args["wordthreads"])
verbose = args["verbose"]

# Load data from file
try:
    with open(host_file) as file:
        host_list = file.read().strip().split('\n')
    with open(path_file) as file:
        path_list = file.read().strip().split('\n')
    print ("[*] Hosts: " + str(len(host_list)) )
    print ("[*] Paths: " + str(len(path_list)) )
except IOError:
    print ("[!] Error: Coudn't read input file")
    sys.exit(1)

# Check if port is open
def check_port(host,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        status = s.connect_ex((host, port))
        s.close()
        if status == 0:
            if verbose: print ("[*] Port open: " + str(host) + " - " + str(port))
            return 1
        else:
            if verbose: print ("[!] Error: Cannot reach " + str(host))
            return 0
    except socket.error:
        if verbose: print ("[!] Error: Cannot reach " + str(host))
        return 0

# Check if path exists
def check_path(host,port,path):
    try:
        if port == 443 or port == 8443:
            url = 'https://' + str(host) + ":" + str(port) + '/' + str(path)
        else:
            url = 'http://' + str(host) + ":" + str(port) + '/' + str(path)

        response = requests.get(url, verify=False, timeout=2, allow_redirects=False)

        if response.status_code == 200:
            title = re.search('(?<=<title>).+?(?=</title>)', response.text, re.DOTALL)
            if title:
                title = title.group().strip()
            else:
                title = ""
            print (str(response.status_code) + "," + str(len(response.content)) + "," + url + "," + title)
        elif verbose:
            print (str(response.status_code) + "," + str(len(response.content)) + "," + url)

    except Exception as e:
        print ("[!] Error: Timeout or unexpected response from " + str(host) + ":" + str(port) + '/' + str(path) )

# Query a single path
def path_worker(host,port,pathq):
    while True:
        path = pathq.get()
        check_path(host,port,path)
        pathq.task_done()

# Create threads for each host
def host_worker(hostq):
    while True:
        host = hostq.get()
        open_ports = []
        for port in port_list:
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
            print ("[*] Host complete: " + str(host) + ":" + str(port))

        hostq.task_done()

def main():

    hostq = Queue()
    threads = []
    for i in range(host_threads):
         t = Thread(target=host_worker,args=(hostq,))
         t.daemon = True
         t.start()
         threads.append(t)

    for host in host_list:
        hostq.put(host)

    hostq.join()


main()
