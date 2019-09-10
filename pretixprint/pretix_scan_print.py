# -*- coding: utf8 -*-

__author__ = "Hauke Webermann"
__copyright__ = "Copyright 2019, webermann.net"
__license__ = "MIT"
__version__ = "0.3.0"
__email__ = "hauke@webermann.net"

import logging
import signal

import serial
import io

from pretixprint.pretix_brother_ql import printLabel
from pretixprint.pretix_user_sync import syncEvents, syncEventData, findUser
from pretixprint.pretix_user_sync import getEventName

from pprint import pprint

CONFIG = {
    'serial': 'COM3',
}

logging.basicConfig(level=logging.ERROR)

global ser


def sigint_handler(signum, frame):
    global ser
    ser.close()
    exit()


def main():
    signal.signal(signal.SIGINT, sigint_handler)

    global ser
    ser = serial.Serial(CONFIG['serial'], 115200, timeout=1)
    ser_io = io.TextIOWrapper(io.BufferedRWPair(ser, ser, 1), newline='\r', line_buffering=True)

    syncEvents()
    syncEventData()

    print('Scan QR Code')

    while True:
        qr = ser_io.readline()
        if len(qr) == 0:
            continue
        qr = qr[:-1]  # Cut \r

        # Find user
        user = findUser(qr)
        if not user:
            print('User not found!')
        else:
            print("Name: " + user[u'Name'])
            print("Ticket: " + user['Tickets'])
            if 'Alter' in user:
                if user[u'Alter'] < 18:
                    print("\nTeilnehmerIn unter 18 Jahre!\n")
            # Print Label
            printLabel(user, getEventName())

    exit()


if __name__ == "__main__":
    main()
