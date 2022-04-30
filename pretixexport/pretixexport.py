# -*- coding: utf8 -*-

__author__ = "Hauke Webermann"
__copyright__ = "Copyright 2019-2022, webermann.net"
__license__ = "MIT"
__version__ = "0.7.0"
__email__ = "hauke@webermann.net"

import time
import sys
import os
import urllib3

from dateutil import parser
import dateutil

from collections import OrderedDict
from operator import itemgetter

import requests
import json
import math

import pickle

from pprint import pprint


startTime = time.time()

reload(sys)
sys.setdefaultencoding('utf-8')

# TODO https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
urllib3.disable_warnings()

if 'PRETIX_API_KEY' in os.environ:
    pretixApiKey = os.environ['PRETIX_API_KEY']
else:
    print("PRETIX_API_KEY not set!")
    exit()

enableSendToSlack = False

if 'PRETIX_SLACK_WEBHOOK' in os.environ:
    slack_webhook = os.environ["PRETIX_SLACK_WEBHOOK"]
    enableSendToSlack = True
else:
    print("PRETIX_SLACK_WEBHOOK not set!")

registrationHistory = {"2015": {
        "06-01": 18, "06-07": 18, "06-09": 19, "06-10": 19,
        "06-12": 21, "06-13": 22, "06-14": 25, "06-15": 26,
        "06-16": 27, "06-17": 30, "06-19": 30, "06-21": 30,
        "06-23": 33, "06-24": 35, "06-26": 37, "06-28": 40,
        "06-29": 43, "06-30": 48, "07-01": 49, "07-02": 50,
        "07-04": 51, "07-06": 62, "07-07": 65, "07-08": 70,
        "07-10": 72, "07-12": 72, "07-13": 76, "07-14": 77,
        "07-15": 78, "07-16": 79, "07-17": 80, "07-18": 81,
        "07-19": 84, "07-20": 85, "07-21": 95, "07-22": 100,
        "07-23": 102, "07-25": 104, "07-26": 112, "07-27": 116,
        "07-28": 118, "07-29": 119, "07-31": 119, "08-01": 121,
        "08-02": 124, "08-03": 125, "08-04": 133, "08-05": 134,
        "08-06": 138, "08-07": 144, "08-08": 147, "08-09": 149,
        "08-10": 152, "08-11": 160, "08-12": 161, "08-13": 165,
        "08-14": 168, "08-15": 173, "08-16": 178, "08-17": 183,
        "08-18": 189, "08-19": 194, "08-20": 198, "08-21": 201,
        "08-22": 214, "08-23": 240, "08-24": 248, "08-25": 257,
        "08-26": 258, "08-27": 262, "08-28": 272, "08-29": 274,
        "08-30": 283, "08-31": 292, "09-01": 299, "09-02": 307,
        "09-03": 312, "09-04": 318, "09-05": 321, "09-06": 330,
        "09-07": 333, "09-08": 344, "09-09": 348, "09-10": 367,
        "09-11": 369, "09-12": 381, "09-13": 387, "09-14": 393,
        "09-15": 402, "09-16": 406
    },
    "2016": {
        "06-01": 13, "06-02": 16, "06-04": 16, "06-06": 19,
        "06-07": 20, "06-08": 25, "06-10": 25, "06-11": 25,
        "06-13": 27, "06-15": 27, "06-17": 27, "06-19": 27,
        "06-20": 28, "06-22": 28, "06-23": 29, "06-25": 30,
        "06-27": 31, "06-29": 31, "06-30": 32, "07-01": 34,
        "07-03": 35, "07-05": 35, "07-07": 35, "07-08": 37,
        "07-10": 38, "07-11": 39, "07-13": 40, "07-14": 42,
        "07-15": 43, "07-16": 44, "07-17": 45, "07-18": 46,
        "07-19": 47, "07-20": 48, "07-21": 51, "07-23": 51,
        "07-25": 51, "07-26": 53, "07-27": 57, "07-28": 59,
        "07-29": 61, "07-30": 62, "07-31": 67, "08-01": 69,
        "08-02": 73, "08-03": 75, "08-04": 80, "08-05": 83,
        "08-06": 86, "08-07": 94, "08-08": 97, "08-09": 105,
        "08-10": 108, "08-11": 115, "08-12": 120, "08-13": 122,
        "08-14": 136, "08-15": 146, "08-16": 152, "08-17": 167,
        "08-18": 177, "08-19": 185, "08-20": 191, "08-21": 217,
        "08-22": 226, "08-23": 234, "08-24": 243, "08-25": 257,
        "08-26": 266, "08-27": 281, "08-28": 323, "08-29": 338,
        "08-30": 361, "08-31": 367, "09-01": 370, "09-02": 378,
        "09-03": 385, "09-04": 395, "09-05": 402, "09-06": 411,
        "09-07": 417, "09-08": 427, "09-09": 430, "09-10": 435,
        "09-11": 441, "09-12": 451, "09-13": 466, "09-14": 472,
        "09-15": 472, "09-16": 472
    },
    "2017": {
        "06-01": 0, "06-12": 0, "06-13": 3, "06-15": 4,
        "06-17": 6, "06-18": 7, "06-20": 7, "06-21": 8,
        "06-23": 8, "06-25": 8, "06-26": 8, "06-28": 8,
        "06-30": 9, "07-01": 10, "07-03": 10, "07-05": 10,
        "07-07": 10, "07-09": 11, "07-11": 11, "07-13": 11,
        "07-15": 11, "07-17": 11, "07-19": 11, "07-20": 13,
        "07-21": 15, "07-22": 17, "07-23": 18, "07-24": 20,
        "07-25": 21, "07-27": 21, "07-28": 22, "07-29": 24,
        "07-30": 25, "07-31": 29, "08-01": 34, "08-02": 38,
        "08-03": 39, "08-04": 41, "08-05": 43, "08-06": 48,
        "08-07": 53, "08-08": 57, "08-09": 60, "08-10": 64,
        "08-11": 65, "08-12": 75, "08-13": 85, "08-14": 89,
        "08-15": 93, "08-16": 108, "08-17": 133, "08-18": 151,
        "08-19": 174, "08-20": 224, "08-21": 233, "08-22": 262,
        "08-23": 282, "08-24": 287, "08-25": 288, "08-26": 290,
        "08-27": 293, "08-28": 297, "08-29": 303, "08-30": 309,
        "08-31": 315, "09-01": 320, "09-02": 326, "09-03": 337,
        "09-04": 340, "09-05": 352, "09-06": 355, "09-07": 357,
        "09-08": 366, "09-09": 378, "09-10": 383, "09-11": 394,
        "09-12": 404, "09-13": 415, "09-14": 415, "09-15": 415,
        "09-16": 415
    },
    "2018": {
        "06-01": 0, "06-09": 0, "06-10": 1, "06-11": 2,
        "06-20": 2, "06-21": 3, "07-02": 3, "07-03": 4,
        "07-04": 6, "07-06": 8, "07-09": 8, "07-10": 10,
        "07-15": 10, "07-16": 11, "07-17": 13, "07-19": 14,
        "07-21": 14, "07-22": 15, "07-23": 20, "07-24": 21,
        "07-25": 22, "07-26": 23, "07-28": 24, "07-29": 27,
        "07-30": 30, "07-31": 33, "08-01": 36, "08-02": 40,
        "08-03": 41, "08-04": 44, "08-05": 53, "08-06": 56,
        "08-07": 58, "08-08": 72, "08-09": 78, "08-10": 83,
        "08-11": 88, "08-12": 93, "08-13": 97, "08-14": 101,
        "08-15": 106, "08-16": 112, "08-17": 115, "08-18": 125,
        "08-19": 143, "08-20": 156, "08-21": 184, "08-22": 256,
        "08-23": 276, "08-24": 285, "08-25": 290, "08-26": 298,
        "08-27": 305, "08-28": 310, "08-29": 314, "08-30": 318,
        "08-31": 323, "09-01": 327, "09-02": 329, "09-03": 335,
        "09-04": 343, "09-05": 348, "09-06": 352, "09-07": 357,
        "09-08": 361, "09-09": 368, "09-10": 370, "09-11": 384,
        "09-12": 390, "09-13": 397, "09-14": 399, "09-15": 420
    },
    "2019": {
        "06-28": 9, "06-29": 15, "06-30": 18, "07-01": 22,
        "07-03": 23, "07-04": 24, "07-05": 25, "07-06": 28,
        "07-09": 29, "07-14": 31, "07-15": 32, "07-16": 33,
        "07-17": 42, "07-18": 44, "07-19": 46, "07-20": 47,
        "07-21": 48, "07-22": 52, "07-23": 56, "07-25": 57,
        "07-26": 59, "07-27": 61, "07-28": 62, "07-29": 64,
        "07-30": 65, "08-01": 69, "08-05": 71, "08-06": 73,
        "08-08": 74, "08-09": 83, "08-10": 85, "08-11": 89,
        "08-12": 95, "08-13": 101, "08-14": 107, "08-15": 119,
        "08-16": 133, "08-17": 158, "08-18": 203, "08-19": 208,
        "08-20": 221, "08-21": 253, "08-22": 254, "08-23": 259,
        "08-24": 262, "08-26": 264, "08-27": 273, "08-28": 275,
        "08-29": 278, "08-31": 283, "09-01": 289, "09-02": 297,
        "09-03": 301, "09-04": 305, "09-05": 309, "09-06": 312,
        "09-07": 317, "09-08": 325, "09-09": 337, "09-10": 345,
        "09-11": 361, "09-12": 367, "09-13": 375, "09-14": 387
    }
}

html = open("index.html", "w")
html.write("""
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
<title>Pretix Export</title>

<style>
html, body {
    font-family: Verdana,sans-serif;
    font-size: 12px;
    line-height: 1.5;
    padding: 5px;
}
table {
    width: 100%;
}
table, th, td {
    border: 1px solid #ccc;
    border-collapse: collapse;
    border-spacing: 0;
    padding: 6px 8px;
}
table tr:nth-child(even) {
    background-color: #eee;
}
table tr:nth-child(odd) {
   background-color:#fff;
}
.ec_graphbar {
    background:     rgb(15, 112, 183) !important;
    height:         10px;
    float: left;
}
.ec_graphbarInvert {
    background:     rgb(112, 183, 15) !important;
    height:         10px;
    overflow: hidden;
}
.ec_graphbar_border {
    border:         rgb(15, 112, 183) solid 1px;
    overflow: hidden;
}
</style>
<!-- Plotly.js -->
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
""")


def dictInc(d, name):
    d[name] = d.get(name, 0) + 1


def printUl(list, strDict=None, withPercent=False):
    # pprint(strDict)

    if not list:
        html.write('<p>Keine Daten.</p>')
    else:
        _sum = 0
        if withPercent:
            for _key, _value in list.items():
                _sum += _value

        html.write('<ul>')
        for _key, _value in list.items():
            if _value != 0:
                if strDict == None:
                    html.write('<li>' + str(_key) + ': ' + str(_value))
                else:
                    html.write('<li>' + str(strDict[_key]) + ': ' + str(_value))

                if withPercent:
                    html.write(' (' + "{:.1f}".format(100.0 * _value / _sum) + ' %)')
                html.write('</li>')
        html.write('</ul>')


def printSeminarTable(list):
    if not list:
        html.write('<p>Keine Daten.</p>')
    else:
        html.write('<table>')

        for _key, _value in list.items():
            seminar = products[_key]

            if not isinstance(_value, dict):
                html.write('<tr>')
                html.write('<td>' + seminar['name'][u'de-informal'] + ': ' + str(_value) + ' (' + str(
                    quotas[seminar['id']][u'size']) + ')</td>')
                html.write('<td width="205">')
                printBar(_value, quotas[seminar['id']][u'size'])
                html.write('</td>')
                html.write('</tr>')
            else:
                continue

        html.write('</table>')


def printBar(value, limit, addSecond=False):
    barSize = 200
    barWidth = 0
    if limit != 0:
        barWidth = math.floor(200 * value / limit)
    html.write('<div class="ec_graphbar_border" style="width: ' + str(barSize) + 'px;">')
    html.write('<div class="ec_graphbar" style="width: ' + str(barWidth) + 'px;"></div>')
    if addSecond:
        html.write('<div class="ec_graphbarInvert" style="width: ' + str(barSize - barWidth) + 'px;"></div>')
    html.write('</div>')


def genTraceVarStr(list, type, name, show=True, line_width=2):
    """var
    trace1 = {
        x: [1, 2, 3, 4],
        y: [10, 15, 13, 17],
        type: 'scatter',
        name: 'Text'
    };"""
    x = ""
    y = ""

    for key, val in list.items():
        x += '"' + str(key) + '", '
        y += str(val) + ', '

    out = "var trace" + name.replace(" ", "_") + " = {\n"
    out += "x: [" + x + "],\n"
    out += "y: [" + y + "],\n"
    out += "type: \"" + type + "\",\n"
    out += "hoverinfo: \"y\",\n"
    if not show:
        out += "visible: \"legendonly\",\n"
    out += "line: {width:" + str(line_width) + "},\n"
    out += "name: \"" + name + "\""
    out += "};"

    return out


def sendToSlack(message):
    slackHeaders = {'Content-type': 'application/json'}
    if message:
        slackData = {'text': message}
        requests.post(slack_webhook, data=json.dumps(slackData), headers=slackHeaders)


baseUrl = 'https://tickets.ec-niedersachsen.de/api/v1/organizers/ec-nds/'

headers = {
    'Authorization': 'Token ' + pretixApiKey,
    'content-type': 'application/json; charset=utf-8'
}

response = requests.get(baseUrl + 'events/', headers=headers, verify=False)
eventData = response.json()
# pprint(eventData)

if eventData['count'] == 0:
    print('No events.')
    exit()

print('Found ' + str(eventData['count']) + ' events')

# event = eventData['results'][-1]
for event in eventData['results']:
    if not event['live']:
        continue
    print(event['slug'])
    if 'connect' not in event['slug']:
        continue

    stats = {
        'users': {},
        'products': {},
        'answers': {},
        'stats': {
            'count': {
                'Samstag': 0,
                'Sonntag': 0},
            'status': {},
            'dateRegistration': {},
            'datePayment': {},
            'payment': {},
            'age': {},
            'ageAvg': 0,
            'overnight': {
                u'männlich': 0,
                u'weiblich': 0},
        }
    }
    strData = {
        'product': {},
        'variant': {},
        'question': {},
    }

    eventSlug = event['slug']
    eventName = event['name']['de-informal']
    eventUrl = baseUrl + 'events/' + eventSlug + '/'
    eventDate = parser.parse(event[u'date_from'])
    # pprint(event)

    html.write('<h1>' + eventName + '</h1>')
    print('Get statistics from ' + eventName + ' (' + eventSlug + ')')

    """ Categories """
    response = requests.get(eventUrl + 'categories/', headers=headers, verify=False)
    categoryData = response.json()
    # pprint(categoryData)
    print('Found ' + str(categoryData['count']) + ' categories')
    categories = {}
    categories_map = {}
    for category in categoryData['results']:
        categories[category['id']] = category
        categories_map[category['name']['de-informal']] = category['id']

    """ Items or Products """
    response = requests.get(eventUrl + 'items/', headers=headers, verify=False)
    productData = response.json()
    # pprint(productData)
    print('Found ' + str(productData['count']) + ' products')
    products = {}
    products_map = {}
    variations = {}
    for product in productData['results']:
        print('id ' + str(product['id']) + ' -> ' + product['name']['de-informal'])
        strData['product'][product['id']] = product['name']['de-informal']
        products[product['id']] = product
        products_map[product['name']['de-informal']] = product['id']
        if not (product['category'] in stats['products']):
            stats['products'][product['category']] = {}

        """ Variations """
        response = requests.get(eventUrl + 'items/' + str(product['id']) + '/variations/', headers=headers, verify=False)
        variantData = response.json()
        # pprint(variantData)
        variations[product['id']] = {}
        for variant in variantData['results']:
            variations[product['id']][variant['id']] = variant
            stats['products'][product['category']][product['id']] = {}
            strData['variant'][variant['id']] = variant['value']['de-informal']

    """ Questions """
    response = requests.get(eventUrl + 'questions/', headers=headers, verify=False)
    questionData = response.json()
    # pprint(questionData)
    print('Found ' + str(questionData['count']) + ' questions')
    questions = {}
    questions_map = {}
    options_map = {}
    for question in questionData['results']:
        print('id ' + str(question['id']) + ' -> ' + question['question']['de-informal'])
        questions[question['id']] = question
        questions_map[question['question']['de-informal']] = question['id']

        if not question['options']:
            stats['answers'][question['id']] = 0
        else:
            for option in question['options']:
                print('    id ' + str(option['id']) + ' -> ' + option['answer']['de-informal'])
                options_map[option['answer']['de-informal']] = option['id']

                if not (question['id'] in stats['answers']):
                    stats['answers'][question['id']] = {}
                    strData['question'][question['id']] = {}

                stats['answers'][question['id']][option['id']] = 0
                strData['question'][question['id']][option['id']] = option['answer']['de-informal']

    """ Quotas """
    response = requests.get(eventUrl + 'quotas/', headers=headers, verify=False)
    quotaData = response.json()
    # pprint(quotaData)
    print('Found ' + str(quotaData['count']) + ' quotas')
    quotas = {}
    for quota in quotaData['results']:
        for productId in quota['items']:
            quotas[productId] = quota

    """ Orders """
    numberOfRegistrationWithoutBirthday = 0
    orderUrl = eventUrl + 'orders/'
    while True:
        for timeout in range(0, 10):
            response = requests.get(orderUrl, headers=headers, verify=False)
            print("Get response " + str(response) + " requesting " + orderUrl)
            if response.status_code == 200:
                break

        orderData = response.json()
        # pprint(orderData['results'][6])
        print('Found ' + str(orderData['count']) + ' orders')

        # Order Status
        # n – pending
        # p – paid
        # e – expired
        # c – canceled
        # r – refunded

        for order in orderData['results']:
            dictInc(stats['stats']['status'], order['status'])

            if (order['status'] != 'c') and (order['status'] != 'r'):
                user = {
                    u'Auch wenn ich das ganze Wochenende gebucht habe, übernachte ich nicht im Connect-Quartier.': 'False',
                    u'E-Mail': order['email']
                }

                dt = parser.parse(order['datetime'])
                dictInc(stats['stats']['dateRegistration'], str(dt.date()))

                if isinstance(order[u'payment_date'], basestring):
                    dt = parser.parse(order[u'payment_date'])
                    dictInc(stats['stats']['datePayment'], str(dt.date()))

                dictInc(stats['stats']['payment'], order['payment_provider'])

                for position in order['positions']:
                    if position['attendee_name'] is not None:
                        user[u'Name'] = position['attendee_name']

                    user[categories[products[position['item']]['category']]['name']['de-informal']] = \
                        products[position['item']]['name']['de-informal']

                    if position['variation'] is not None:
                        user[categories[products[position['item']]['category']]['name']['de-informal']] += ' ' + \
                             variations[position['item']][position['variation']]['value']['de-informal']
                        dictInc(stats['products'][products[position['item']]['category']][position['item']],
                                position['variation'])
                    else:
                        dictInc(stats['products'][products[position['item']]['category']], position['item'])

                    for answers in position['answers']:
                        user[questions[answers['question']]['question']['de-informal']] = answers['answer']

                        if not isinstance(stats['answers'][answers['question']], dict):
                            if answers['answer'] != 'False':
                                stats['answers'][answers['question']] += 1
                        else:
                            for option in answers['options']:
                                stats['answers'][answers['question']][option] += 1

                if (user[u'Auch wenn ich das ganze Wochenende gebucht habe, übernachte ich nicht im Connect-Quartier.'] == 'False') and ('Wochenende' in user['Tickets']):
                    dictInc(stats['stats']['overnight'], user['Geschlecht'])

                if u'Geburtsdatum' in user:
                    dt = parser.parse(user[u'Geburtsdatum'])
                    age = dateutil.relativedelta.relativedelta(eventDate.date(), dt.date())
                    dictInc(stats['stats']['age'], age.years)
                    user[u'Alter'] = age.years
                    stats['stats']['ageAvg'] += age.years
                else:
                    numberOfRegistrationWithoutBirthday += 1

                stats['users'][order['code']] = user

        if orderData['next']:
            orderUrl = orderData['next']
        else:
            break

    numberOfRegistration = len(stats['users'])
    if numberOfRegistration != 0:
        stats['stats']['ageAvg'] /= float(numberOfRegistration)

    # pprint(categories_map)
    CATEGORY_TICKETS = categories_map[u'Tickets']
    CATEGORY_SEMINARS = categories_map[u'Seminare und Workshops']
    #CATEGORY_SHIRTS = categories_map[u'Connect 2019 T-Shirt']
    CATEGORY_KV_SPECIAL = categories_map[u'Anreise aus dem Kreisverband']
    #CATEGORY_BECHER = categories_map[u'Connect Becher']

    for idx, value in stats['products'][CATEGORY_TICKETS].items():
        if 'Wochenende' in products[idx][u'name'][u'de-informal']:
            stats['stats']['count']['Samstag'] += value
            stats['stats']['count']['Sonntag'] += value
        if 'Samstag' in products[idx][u'name'][u'de-informal']:
            stats['stats']['count']['Samstag'] += value

    # pprint(stats['answers'])
    # pprint(stats['stats'])
    # pprint(stats['products'])
    # pprint(strData)

    # pprint(questions_map)
    # pprint(products_map)

    html.write('<h2>Statistik</h2>')
    for key, category in categories.items():
        html.write('<h3>' + category['name']['de-informal'] + '</h3>')
        printSeminarTable(stats['products'][key])

    #html.write('<h4>T-Shirts (Frauen) Größe</h4>')
    #printUl(stats['products'][CATEGORY_SHIRTS][products_map[u'T-Shirt Frauen']], strData['variant'])
    #html.write('<h4>T-Shirts (Männer) Größe</h4>')
    #printUl(stats['products'][CATEGORY_SHIRTS][products_map[u'T-Shirt Männer / Unisex']], strData['variant'])

    html.write('<h3>Teilnehmer</h3>')
    printUl(stats['stats']['count'])

    html.write('<h3>Catering</h3>')
    questionCatering = questions_map[u'Die Verpflegung ist im Ticket enthalten. Besondere Wünsche bitte hier angeben']
    printUl(stats['answers'][questionCatering], strData['question'][questionCatering])

    html.write('<h4>Geschlecht</h4>')
    printBar(stats['answers'][questions_map['Geschlecht']][options_map['weiblich']], numberOfRegistration, True)
    printUl(stats['answers'][questions_map['Geschlecht']], strData['question'][questions_map['Geschlecht']], withPercent=True)

    html.write('<h4>Quartier benötigt</h4>')
    sumOfQuartier = stats['stats']['overnight'][u'männlich'] + stats['stats']['overnight'][u'weiblich']
    printBar(sumOfQuartier, numberOfRegistration, True)
    printUl({0: sumOfQuartier}, {0: 'Übernachtungen'})
    printBar(stats['stats']['overnight'][u'männlich'], sumOfQuartier, True)
    printUl(stats['stats']['overnight'], withPercent=True)

    html.write('<h4>Anreise</h4>')
    printUl(stats['answers'][questions_map['Anreise']], strData['question'][questions_map['Anreise']], withPercent=True)

    html.write('<h4>Alter</h4>')
    stats['stats']['age'] = OrderedDict(sorted(stats['stats']['age'].items()))
    html.write('<div id="chartAge"></div>')
    html.write('<p>Durchschnitt: ' + "{:.1f}".format(stats['stats']['ageAvg']) + ' Jahre</p>')

    html.write("\n<script>")
    html.write(genTraceVarStr(stats['stats']['age'], 'bar', 'Alter'))
    html.write("""
        var data = [traceAlter];
        Plotly.newPlot('chartAge', data, {width: 700}, {showSendToCloud: false});
    </script>""")

    html.write('<h4>EC-Mitglied</h4>')
    printUl(stats['answers'][questions_map['EC-Mitglied?']], strData['question'][questions_map['EC-Mitglied?']], withPercent=True)

    html.write('<h4>EC-Ort</h4>')
    questionECOrt = questions_map['EC / Gemeinde']
    stats['answers'][questionECOrt] = OrderedDict(sorted(stats['answers'][questionECOrt].items(), key=itemgetter(1), reverse=True))
    printUl(stats['answers'][questionECOrt], strData['question'][questionECOrt])

    html.write('<h4>Sommer Freizeit</h4>')
    questionFreizeit = questions_map['Ich bin in diesem Sommer auf folgender Freizeit:']
    printUl(stats['answers'][questionFreizeit], strData['question'][questionFreizeit])

    html.write('<h4>Anmeldungen pro Tag</h4>')
    stats['stats']['dateRegistration'] = OrderedDict(sorted(stats['stats']['dateRegistration'].items()))
    stats['stats']['datePayment'] = OrderedDict(sorted(stats['stats']['datePayment'].items()))

    sum = 0
    traceReg = {}

    for date, cnt in stats['stats']['dateRegistration'].items():
        d = parser.parse(date)
        sum += cnt
        traceReg[d.strftime('%Y-%m-%d')] = sum

    sum = 0
    tracePaid = {}

    for date, cnt in stats['stats']['datePayment'].items():
        d = parser.parse(date)
        sum += cnt
        tracePaid[d.strftime('%Y-%m-%d')] = sum

    traceReg = OrderedDict(sorted(traceReg.items()))
    tracePaid = OrderedDict(sorted(tracePaid.items()))

    html.write('<div id="chartRegistration"></div>')
    html.write("\n<script>")
    html.write(genTraceVarStr(traceReg, 'scatter', 'Anmeldungen', True, 4))
    html.write(genTraceVarStr(tracePaid, 'scatter', 'Bezahlt'))

    eventYear = eventDate.strftime('%Y')
    historyTraces = ""

    for year, yearData in registrationHistory.items():
        trace = {}
        for idx, val in yearData.items():
            trace[str(eventYear) + "-" + idx] = val

        trace = OrderedDict(sorted(trace.items()))
        html.write(genTraceVarStr(trace, 'scatter', "Anmeldung " + str(year), False))
        historyTraces += "traceAnmeldung_" + str(year) + ", "

    html.write("""
        var data = [traceAnmeldungen, traceBezahlt, """ + historyTraces + """];
        Plotly.newPlot('chartRegistration', data, {width: 1000}, {showSendToCloud: false, locale: 'de'});
    </script>""")

    html.write('<h4>Bezahlung</h4>')
    printUl(stats['stats']['payment'], withPercent=True)

    html.write('<h4>Status</h4>')
    printUl(stats['stats']['status'], {'n': 'pending', 'p': 'paid', 'e': 'expired', 'c': 'canceled', 'r': 'refunded'},
            withPercent=True)

    """ Send info to Slack """
    if enableSendToSlack:
        ordersListLast = []
        fileName = 'orders.p'
        if os.path.exists(fileName):
            with open(fileName, 'rb') as fp:
                ordersListLast = pickle.load(fp)

        for idx, user in stats['users'].items():
            if not (idx in ordersListLast):
                message = 'Neue Anmeldung *' + user['Tickets'] + '* ' + idx + "\n"
                message += '*' + user['Name'] + '*'

                if 'Ort' in user.keys():
                    message += ' aus ' + user['Ort']

                if 'EC / Gemeinde' in user.keys():
                    message += ' (' + user['EC / Gemeinde'] + ')'

                if 'Alter' in user.keys():
                    message += ' ' + str(user['Alter']) + ' Jahre'

                message += "\n"

                if 'Seminare und Workshops' in user.keys():
                    message += user['Seminare und Workshops'] + "\n"

                if 'Connect 2019 T-Shirt' in user.keys():
                    message += user['Connect 2019 T-Shirt'] + "\n"

                if 'Anreise aus dem Kreisverband' in user.keys():
                    message += user['Anreise aus dem Kreisverband'] + "\n"

                sendToSlack(message)

                ordersListLast.append(idx);

        with open(fileName, 'wb') as fp:
            pickle.dump(ordersListLast, fp)

    """ End HTML file """
    html.write('<p>Version: ' + __version__ +
               '<br />Stand: ' + time.strftime("%d.%m.%Y %H:%M", time.localtime()) +
               '<br />Dauer: ' + "{:.3f} s".format(float(time.time()) - startTime) + '</p>')

html.write("""
</body>
</html>
""")

html.close()
exit()
