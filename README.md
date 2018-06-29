# pyBuster

A simple website path brute-forcer.

Example usage:

`python pyBuster.py -u hosts.txt -w words.txt -v`

Select ports to scan:

`python pyBuster.py -u hosts.txt -w words.txt -v -p 80,443,8443`

Change the number of threads:

`python pyBuster.py -u hosts.txt -w words.txt -v -th 10 -tw 15`

Hosts and words file should be one entry per line:

```
www.test1.com
www.test2.com
192.168.1.2
```


Help:

```
usage: pyBuster.py [-h] -u HOSTLIST -w WORDLIST [-p PORTLIST]
                   [-th HOSTTHREADS] [-tw WORDTHREADS] [-v]

pyBuster a multi-target URL bruteforcer

optional arguments:
  -h, --help            show this help message and exit
  -u HOSTLIST, --hostlist HOSTLIST
                        File containing hosts to test
  -w WORDLIST, --wordlist WORDLIST
                        File containing words/paths to test
  -p PORTLIST, --portlist PORTLIST
                        Comma separated list of ports to test
  -th HOSTTHREADS, --hostthreads HOSTTHREADS
                        Number of concurrent hosts
  -tw WORDTHREADS, --wordthreads WORDTHREADS
                        Number of threads per host
  -v, --verbose         Show more information
```
