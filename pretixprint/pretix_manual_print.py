# -*- coding: utf8 -*-

__author__ = "Hauke Webermann"
__copyright__ = "Copyright 2019, webermann.net"
__license__ = "MIT"
__version__ = "0.2.0"
__email__ = "hauke@webermann.net"

import logging
import signal
from pretixprint.pretix_brother_ql import printLabel

logging.basicConfig(level=logging.ERROR)


def sigint_handler(signum, frame):
    exit()


def main():
    signal.signal(signal.SIGINT, sigint_handler)    
    
    user = {
        'Name': '',
        'Tickets': '',
        'order': 'C19TBM'
    }
    
    while True:
        var = input("Vor und Nachname: ")
        user['Name'] = str(var)
        
        var = input("Ticket (Wochenende, Samstag, Wochenende (Mitarbeiter)): ")
        user['Tickets'] = str(var)
        
        # Print Label
        printLabel(user, 'Connect 2019')

    exit()


if __name__ == "__main__": 
    main()
