# -*- coding: utf8 -*-

__author__ = "Hauke Webermann"
__copyright__ = "Copyright 2018, webermann.net"
__license__ = "MIT"
__version__ = "0.1.1"
__email__ = "hauke@webermann.net"

from brother_ql import BrotherQLRaster
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send

from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

from nameparser import HumanName


CONFIG = {
    'printer': 'QL-810W',
    'identifier': 'usb://0x04f9:0x209c',
    'backend': 'pyusb',
}

imgSize = (900, 540)
fillBlack = (0, 0, 0)
fillWhite = (255, 255, 255)


def printCenter(d, y, text, font):
    textSize = d.textsize(text, font)
    x = (imgSize[0] - textSize[0]) / 2
    d.multiline_text((x, y), text, fillBlack, font=font)


def printLabel(user, eventName, count=1):
    FONT_NAME = "/usr/share/fonts/truetype/DejaVuSans.ttf"
    f25 = ImageFont.truetype(FONT_NAME, 25)
    f40 = ImageFont.truetype(FONT_NAME, 40)
    f80 = ImageFont.truetype(FONT_NAME, 80)
    f100 = ImageFont.truetype(FONT_NAME, 100)

    img = Image.new("RGB", imgSize, fillWhite)
    draw = ImageDraw.Draw(img)

    name = HumanName(user['Name'])
    
    ticket = user['Tickets'].split()
    if 'Abend' in user['Tickets']:
        ticket[0] += ' ' + ticket[1]
    
    mitarbeiter = False
    if 'Mitarbeiter' in user['Tickets']:
        mitarbeiter = True
    if 'Free' in user['Tickets']:
        mitarbeiter = True
    
    printCenter(draw, 50, name.first, f100)
    printCenter(draw, 170, name.last, f40)
    
    if mitarbeiter:
        printCenter(draw, 240, "Mitarbeiter", f80)

    printCenter(draw, 350, ticket[0] + ' (' + user['order'] + ')', f40)
    printCenter(draw, 400, eventName, f40)
    
    if 'Alter' in user:
        printCenter(draw, 450, "Alter: " + str(user['Alter']), f25)

    if 'Seminare und Workshops' in user:
        seminar = user['Seminare und Workshops'].split('(')
        printCenter(draw, 485, seminar[0], f25)

    img.save('tmp.png')

    qlr = BrotherQLRaster(CONFIG['printer'])
    qlr.exception_on_warning = True
    convert(qlr, ['tmp.png'], '54', cut=True, dither=False, compress=True, red=False, dpi_600=False, hq=True, rotate=90)
    for i in range(count):
        send(instructions=qlr.data, printer_identifier=CONFIG['identifier'], backend_identifier=CONFIG['backend'], blocking=True)   


if __name__ == "__main__": 
    user = {
        'Alter': 34,
        'Name': 'Test Tseter',
        'Tickets': 'Wochenende (Mitarbeiter)',
        'order': '12345',
        'Seminare und Workshops': 'Riesenseifenblasen (Test Referent)',
    }
    
    printLabel(user, 'Test Event')
    exit()
