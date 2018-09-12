# -*- coding: utf8 -*-

__author__ = "Hauke Webermann"
__copyright__ = "Copyright 2018, webermann.net"
__license__ = "MIT"
__version__ = "0.3.1"
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
import math

from pprint import pprint


startTime = time.time()

reload(sys)
sys.setdefaultencoding('utf-8')

# TODO https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
urllib3.disable_warnings()

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

.bar-graph {
  padding: 0;
  width: 100%;
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
  -webkit-align-items: flex-end;
      -ms-flex-align: end;
          align-items: flex-end;
  height: 425px;
  margin: 0;
}

.bar-graph li {
  display: block;
  padding: 1.5625rem 0;
  position: relative;
  text-align: center;
  vertical-align: bottom;
  border-radius: 4px 4px 0 0;
  max-width: 20%;
  height: 100%;
  margin: 0 1.8% 0 0;
  -webkit-flex: 1 1 15%;
      -ms-flex: 1 1 15%;
          flex: 1 1 15%;
}

.bar-graph .bar-graph-axis {
  -webkit-flex: 1 1 8%;
      -ms-flex: 1 1 8%;
          flex: 1 1 8%;
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
  -webkit-flex-direction: column;
      -ms-flex-direction: column;
          flex-direction: column;
  -webkit-justify-content: space-between;
      -ms-flex-pack: justify;
          justify-content: space-between;
}

.bar-graph .bar-graph-label {
  margin: 0;
  background-color: none;
  color: #8a8a8a;
  position: relative;
}

@media print, screen and (min-width: 40em) {
  .bar-graph .bar-graph-label:before, .bar-graph .bar-graph-label:after {
    content: "";
    position: absolute;
    border-bottom: 1px dashed #8a8a8a;
    top: 0;
    left: 0;
    height: 50%;
    width: 20%;
  }
}

@media print, screen and (min-width: 40em) and (min-width: 64em) {
  .bar-graph .bar-graph-label:before, .bar-graph .bar-graph-label:after {
    width: 30%;
  }
}

@media print, screen and (min-width: 40em) {
  .bar-graph .bar-graph-label:after {
    left: auto;
    right: 0;
  }
}

.bar-graph .percent {
  letter-spacing: -3px;
  opacity: 0.4;
  width: 100%;
  font-size: 0.5rem;
  position: absolute;
}

@media print, screen and (min-width: 40em) {
  .bar-graph .percent {
    font-size: 0.5rem;
  }
}

.bar-graph .percent span {
  font-size: 1.875rem;
}

.bar-graph .description {
  font-weight: 800;
  opacity: 0.5;
  text-transform: uppercase;
  width: 100%;
  font-size: 14px;
  bottom: 20px;
  position: absolute;
  font-size: 1rem;
  overflow: hidden;
}

.bar-graph .bar.primary {
  border: 1px solid #1779ba;
  background: linear-gradient(#2196e3, #1779ba 70%);
}

.bar-graph .bar.secondary {
  border: 1px solid #767676;
  background: linear-gradient(#909090, #767676 70%);
}

.bar-graph .bar.success {
  border: 1px solid #3adb76;
  background: linear-gradient(#65e394, #3adb76 70%);
}

.bar-graph .bar.warning {
  border: 1px solid #ffae00;
  background: linear-gradient(#ffbe33, #ffae00 70%);
}

.bar-graph .bar.alert {
  border: 1px solid #cc4b37;
  background: linear-gradient(#d67060, #cc4b37 70%);
}
</style>
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
        sum = 0
        if withPercent:
            for key, value in list.items():
                sum += value

        html.write('<ul>')
        for key, value in list.items():
            if value != 0:
                if strDict == None:
                    html.write('<li>' + str(key) + ': ' + str(value))
                else:
                    html.write('<li>' + str(strDict[key]) + ': ' + str(value))

                if withPercent:
                    html.write(' (' + "{:.1f}".format(100.0 * value / sum) + ' %)')
                html.write('</li>')
        html.write('</ul>')


def printSeminarTable(list):
    if not list:
        html.write('<p>Keine Daten.</p>');
    else:
        html.write('<table>');

        for key, value in list.items():
            seminar = products[key]

            if not isinstance(value, dict):
                html.write('<tr>')
                html.write('<td>' + seminar['name'][u'de-informal'] + ': ' + str(value) + ' (' + str(
                    quotas[seminar['id']][u'size']) + ')</td>')
                html.write('<td width="205">')
                printBar(value, quotas[seminar['id']][u'size'])
                html.write('</td>')
                html.write('</tr>')
            else:
                continue

        html.write('</table>')


def printBar(value, limit, addSecond=False):
    barSize = 200
    barWidth = math.floor(200 * value / limit)
    html.write('<div class="ec_graphbar_border" style="width: ' + str(barSize) + 'px;">')
    html.write('<div class="ec_graphbar" style="width: ' + str(barWidth) + 'px;"></div>')
    if addSecond:
        html.write('<div class="ec_graphbarInvert" style="width: ' + str(barSize - barWidth) + 'px;"></div>')
    html.write('</div>')


def printGraph(list):
    rangeMax = 0
    for val in list.items():
        if val[1] > rangeMax:
            rangeMax = val[1]

    rangeMax = int(math.ceil(float(rangeMax) / 10.0) * 10.0)
    print rangeMax

    rangeInc = rangeMax / 5

    html.write('<ul class="bar-graph">')
    html.write('<li class="bar-graph-axis">')

    for i in range(rangeMax, 0 - 1, -rangeInc):
        html.write('<div class="bar-graph-label">' + str(i) + '</div>')

    html.write('</li>')

    for val in list.items():
        html.write('<li class="bar primary" style="height: ' + str(val[1] * 100 / rangeMax) + '%;" title="' +
                   val[0] + ' ' + str(val[1]) + '">')
        html.write('    <div class="percent">' + str(val[1]) + '</div>')
        html.write('</li>')

    html.write('</ul>')


if 'PRETIX_API_KEY' in os.environ:
    pretixApiKey = os.environ['PRETIX_API_KEY']
else:
    print "PRETIX_API_KEY not set!"
    exit()

baseUrl = 'https://tickets.ec-niedersachsen.de/api/v1/organizers/ec-nds/'

headers = {
    'Authorization': 'Token ' + pretixApiKey,
    'content-type': 'application/json; charset=utf-8'
}

response = requests.get(baseUrl + 'events', headers=headers, verify=False)
eventData = response.json()
# pprint(eventData)

if eventData['count'] == 0:
    print 'No events.'
    exit()

print 'Found ' + str(eventData['count']) + ' events'

for event in eventData['results']:
    if not event['live']:
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
            'overnight': {},
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
    print 'Get statistics from ' + eventName + ' (' + eventSlug + ')'

    """ Categories """
    response = requests.get(eventUrl + 'categories', headers=headers, verify=False)
    categoryData = response.json()
    # pprint(categoryData)
    print 'Found ' + str(categoryData['count']) + ' categories'
    categories = {}
    for category in categoryData['results']:
        categories[category['id']] = category

    """ Items or Products """
    response = requests.get(eventUrl + 'items', headers=headers, verify=False)
    productData = response.json()
    # pprint(productData)
    print 'Found ' + str(productData['count']) + ' products'
    products = {}
    variations = {}
    for product in productData['results']:
        print 'id ' + str(product['id']) + ' name ' + product['name']['de-informal']
        strData['product'][product['id']] = product['name']['de-informal']
        products[product['id']] = product
        if not (product['category'] in stats['products']):
            stats['products'][product['category']] = {}

        """ Variations """
        response = requests.get(eventUrl + 'items/' + str(product['id']) + '/variations', headers=headers, verify=False)
        variantData = response.json()
        # pprint(variantData)
        variations[product['id']] = {}
        for variant in variantData['results']:
            variations[product['id']][variant['id']] = variant
            stats['products'][product['category']][product['id']] = {}
            strData['variant'][variant['id']] = variant['value']['de-informal']

    """ Questions """
    response = requests.get(eventUrl + 'questions', headers=headers, verify=False)
    questionData = response.json()
    # pprint(questionData)
    print 'Found ' + str(questionData['count']) + ' questions'
    questions = {}
    for question in questionData['results']:
        print 'id ' + str(question['id']) + ' name ' + question['question']['de-informal']
        questions[question['id']] = question
        if not question['options']:
            stats['answers'][question['id']] = 0
        else:
            for option in question['options']:
                print '    id ' + str(option['id']) + ' name ' + option['answer']['de-informal']

                if not (question['id'] in stats['answers']):
                    stats['answers'][question['id']] = {}
                    strData['question'][question['id']] = {}

                stats['answers'][question['id']][option['id']] = 0
                strData['question'][question['id']][option['id']] = option['answer']['de-informal']

    """ Quotas """
    response = requests.get(eventUrl + 'quotas', headers=headers, verify=False)
    quotaData = response.json()
    # pprint(quotaData)
    print 'Found ' + str(quotaData['count']) + ' quotas'
    quotas = {}
    for quota in quotaData['results']:
        for productId in quota['items']:
            quotas[productId] = quota

    """ Orders """
    numberOfRegistrationWithoutBirthday = 0
    orderUrl = eventUrl + 'orders'
    while True:
        response = requests.get(orderUrl, headers=headers, verify=False)
        orderData = response.json()
        # pprint(orderData['results'][6])
        print 'Found ' + str(orderData['count']) + ' orders'

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

    stats['stats']['ageAvg'] /= float(numberOfRegistration)

    for idx, value in stats['products'][1].items():
        if 'Wochenende' in products[idx][u'name'][u'de-informal']:
            stats['stats']['count']['Samstag'] += value
            stats['stats']['count']['Sonntag'] += value
        if 'Samstag' in products[idx][u'name'][u'de-informal']:
            stats['stats']['count']['Samstag'] += value

    # pprint(stats['answers'])
    # pprint(stats['stats'])
    # pprint(stats['products'])
    # pprint(strData)

    html.write('<h2>Statistik</h2>')
    for key, category in categories.items():
        html.write('<h3>' + category['name']['de-informal'] + '</h3>')
        printSeminarTable(stats['products'][key])

    html.write('<h4>T-Shirts (Frauen) Größe</h4>')
    printUl(stats['products'][3][40], strData['variant'])
    html.write('<h4>T-Shirts (Männer) Größe</h4>')
    printUl(stats['products'][3][9], strData['variant'])

    html.write('<h3>Teilnehmer</h3>')
    printUl(stats['stats']['count'])

    html.write('<h3>Catering</h3>')
    printUl(stats['answers'][9], strData['question'][9])

    html.write('<h4>Geschlecht</h4>')
    printBar(stats['answers'][1][1], numberOfRegistration, True)
    printUl(stats['answers'][1], strData['question'][1], withPercent=True)

    html.write('<h4>Quartier benötigt</h4>')
    printBar(numberOfRegistration - stats['answers'][8], numberOfRegistration, True)
    printUl({0: numberOfRegistration - stats['answers'][8]}, {0: 'Übernachtungen'})
    printBar(stats['stats']['overnight'][u'männlich'], numberOfRegistration - stats['answers'][8], True)
    printUl(stats['stats']['overnight'], withPercent=True)

    html.write('<h4>Anreise</h4>')
    printUl(stats['answers'][11], strData['question'][11], withPercent=True)

    html.write('<h4>Alter</h4>')
    stats['stats']['age'] = OrderedDict(sorted(stats['stats']['age'].items()))
    printUl(stats['stats']['age'])
    html.write('<p>Durchschnitt: ' + "{:.1f}".format(stats['stats']['ageAvg']) + ' Jahre</p>')

    html.write('<h4>EC-Mitglied</h4>')
    printUl(stats['answers'][7], strData['question'][7], withPercent=True)

    html.write('<h4>EC-Ort</h4>')
    stats['answers'][6] = OrderedDict(sorted(stats['answers'][6].items(), key=itemgetter(1), reverse=True))
    printUl(stats['answers'][6], strData['question'][6])

    html.write('<h4>Sommer Freizeit</h4>')
    printUl(stats['answers'][10], strData['question'][10])

    html.write('<h4>Anmeldungen pro Monat</h4>')
    stats['stats']['dateRegistration'] = OrderedDict(sorted(stats['stats']['dateRegistration'].items()))
    stats['stats']['datePayment'] = OrderedDict(sorted(stats['stats']['datePayment'].items()))
    printUl(stats['stats']['dateRegistration'])
    # printGraph(stats['stats']['dateRegistration'])

    html.write('<h4>Bezahlung</h4>')
    printUl(stats['stats']['payment'], withPercent=True)

    html.write('<h4>Status</h4>')
    printUl(stats['stats']['status'], {'n': 'pending', 'p': 'paid', 'e': 'expired', 'c': 'canceled', 'r': 'refunded'},
            withPercent=True)

    html.write('<p>Version: ' + __version__ +
               '<br />Stand: ' + time.strftime("%d.%m.%Y %H:%M", time.localtime()) +
               '<br />Dauer: ' + "{:.3f} s".format(float(time.time()) - startTime) + '</p>')

html.write("""
</body>
</html> 
""")

html.close()
exit()
