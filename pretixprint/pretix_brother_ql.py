# -*- coding: utf8 -*-

__author__ = "Hauke Webermann"
__copyright__ = "Copyright 2019, webermann.net"
__license__ = "MIT"
__version__ = "0.2.0"
__email__ = "hauke@webermann.net"

from brother_ql import BrotherQLRaster
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send

from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

from nameparser import HumanName


CONFIG = {
    'printer': 'QL-800',  # 'printer': 'QL-810W',
    'identifier': 'usb://0x04f9:0x209b',  # 'identifier': 'usb://0x04f9:0x209c',
    'backend': 'pyusb',
}

imgSize = (900, 540)
fillBlack = (0, 0, 0)
fillWhite = (255, 255, 255)


def printLeft(d, x, y, text, font):
    d.multiline_text((x, y), text, fillBlack, font=font)


def printCenter(d, y, text, font):
    textSize = d.textsize(text, font)
    x = (imgSize[0] - textSize[0]) / 2
    d.multiline_text((x, y), text, fillBlack, font=font)


def printLabel(user, eventName):
    FONT_NAME = "/usr/share/fonts/truetype/DejaVuSans.ttf"
    f17 = ImageFont.truetype(FONT_NAME, 17)
    f18 = ImageFont.truetype(FONT_NAME, 18)
    f25 = ImageFont.truetype(FONT_NAME, 25)
    f40 = ImageFont.truetype(FONT_NAME, 40)
    f80 = ImageFont.truetype(FONT_NAME, 80)
    f100 = ImageFont.truetype(FONT_NAME, 100)

    name = HumanName(user['Name'])

    ticket = user['Tickets'].split()
    if 'Abend' in user['Tickets']:
        ticket[0] += ' ' + ticket[1]

    mitarbeiter = False
    if 'Mitarbeiter' in user['Tickets']:
        mitarbeiter = True
    if 'Free' in user['Tickets']:
        mitarbeiter = True

    for i in range(2):
        img = Image.new("RGB", imgSize, fillWhite)
        draw = ImageDraw.Draw(img)

        printCenter(draw, 50, (name.first.capitalize() + ' ' + name.middle.capitalize()).strip(), f100)
        printCenter(draw, 170, name.last.capitalize(), f40)

        if i == 0:
            if mitarbeiter:
                printCenter(draw, 240, "Mitarbeiter", f80)

            printCenter(draw, 350, ticket[0] + ' (' + user['order'] + ')', f40)
            printCenter(draw, 400, eventName, f40)

            if 'Alter' in user:
                printCenter(draw, 450, "Alter: " + str(user['Alter']), f25)

            if 'Seminare und Workshops' in user:
                seminar = user['Seminare und Workshops'].split('(')
                printCenter(draw, 485, seminar[0], f25)
        else:
            text = """
Samstag
11.30 Uhr - “Zwischen Heimweh und Fernsucht”
13.00 Uhr - Mittagessen
14.30 Uhr - Seminare & Workshops
16.30 Uhr - “We will block you”
18.00 Uhr - Abendessen
20.00 Uhr - “Comming Home”
22.00 Uhr - Latenightangebote & Konzerte"""
            printLeft(draw, 0, 240, text, f17)

            text = """
Sonntag
08.00 Uhr - Frühstück
09.30 Uhr - “Dieser Weg wird kein Leichter sein”
12.00 Uhr - Mittagessen
13.30 Uhr - “Ist herzlich Willkommen übertrieben?”
14.30 Uhr - Abreise

Einlass jeweils 15 Minuten vor Veranstaltungsbeginn"""
            printLeft(draw, 450, 240, text, f17)

            text = """
Solltest du Erste Hilfe benötigen, erreichst du das Connect-Notfall-Team unter 
der Telefonnummer 0170 - 27 65 185 oder du meldest dich am Infopoint."""

            printLeft(draw, 0, 450, text, f18)

        img.save('tmp.png')

        qlr = BrotherQLRaster(CONFIG['printer'])
        qlr.exception_on_warning = True
        convert(qlr, ['tmp.png'], '54', cut=True, dither=False, compress=True, red=False, dpi_600=False, hq=True, rotate=90)
        send(instructions=qlr.data, printer_identifier=CONFIG['identifier'], backend_identifier=CONFIG['backend'], blocking=True)


if __name__ == "__main__": 
    user = {
        'Alter': 34,
        'Name': 'Test Tester',
        'Tickets': 'Wochenende (Mitarbeiter)',
        'order': '12345',
        'Seminare und Workshops': 'Riesenseifenblasen (Test Referent)',
    }
    
    printLabel(user, 'Test Event')
    exit()
