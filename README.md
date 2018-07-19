# pyBuster

A multi-target URL bruteforcer. Python2 and Python3 compliant.

Scan a single target:

`python pyBuster.py -u google.com -w words.txt -v`

Scan multiple targets (verbose flag removed as its quite noisy):

`python pyBuster.py -ul hosts.txt -w words.txt`

Select ports to scan:

`python pyBuster.py -u hosts.txt -w words.txt -v -p 80,443,8443`

Change the number of threads:

`python pyBuster.py -u hosts.txt -w words.txt -v -th 20 -tw 2`

Hosts and words file should be one entry per line.

Example host list:

```
www.test1.com
www.test2.com
192.168.1.2
192.168.2.0/24
```

Example word list:

```
backup.zip
test.html
login.php
```


Help:

```
optional arguments:
  -h, --help            show this help message and exit
  -u HOST, --host HOST  Single host to scan (default: None)
  -ul HOSTLIST, --hostlist HOSTLIST
                        File containing multiple hosts to scan (default: None)
  -w WORDLIST, --wordlist WORDLIST
                        File containing words/paths to test (default: None)
  -p PORTS, --ports PORTS
                        Comma separated list of ports to scan (default:
                        80,443)
  -c CODES, --codes CODES
                        Success HTTP codes comma separated (default: 200)
  -r REDIRECT, --redirect REDIRECT
                        Follow redirects (default: False)
  -th HOSTTHREADS, --hostthreads HOSTTHREADS
                        Number of concurrent hosts (default: 10)
  -tw WORDTHREADS, --wordthreads WORDTHREADS
                        Number of threads per host (default: 3)
  -v, --verbose         Show more information (default: None)
```
