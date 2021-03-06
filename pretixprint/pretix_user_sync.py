# -*- coding: utf8 -*-

__author__ = "Hauke Webermann"
__copyright__ = "Copyright 2019, webermann.net"
__license__ = "MIT"
__version__ = "0.1.1"
__email__ = "hauke@webermann.net"

import logging
import os
import requests

import dateutil
from dateutil import parser

import urllib3

from pprint import pprint

CONFIG = {
    'eventSlug': 'connect19'
}

# TODO https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
urllib3.disable_warnings()

if 'PRETIX_API_KEY' in os.environ:
    pretixApiKey = os.environ['PRETIX_API_KEY']
else:
    print("PRETIX_API_KEY not set!")
    exit()

baseUrl = 'https://tickets.ec-niedersachsen.de/api/v1/organizers/ec-nds/'
eventUrl = baseUrl + 'events/' + CONFIG['eventSlug'] + '/'
global eventName
global eventDate
categories = {}
products = {}
variations = {}
questions = {}
quotas = {}

headers = {
    'Authorization': 'Token ' + pretixApiKey,
    'content-type': 'application/json; charset=utf-8'
}

stats = {
    'users': {},
    'products': {},
    'answers': {},
    'stats': {
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


def syncEvents():
    global eventName
    global eventDate

    response = requests.get(baseUrl + 'events', headers=headers, verify=False)
    eventData = response.json()
    # pprint(eventData)

    if eventData['count'] == 0:
        print('No events found.')
        exit()

    print('Found ' + str(eventData['count']) + ' events')

    for event in eventData['results']:
        if not event['live']:
            continue

        if event['slug'] == CONFIG['eventSlug']:
            eventName = event['name']['de-informal']
            eventDate = parser.parse(event[u'date_from'])
            return

    print('Event not found!')
    exit()


def syncEventData():
    global eventName

    print('Get statistics from ' + eventName + ' (' + CONFIG['eventSlug'] + ')')

    """ Categories """
    response = requests.get(eventUrl + 'categories', headers=headers, verify=False)
    categoryData = response.json()
    # pprint(categoryData)
    print('Found ' + str(categoryData['count']) + ' categories')

    for category in categoryData['results']:
        categories[category['id']] = category

    """ Items or Products """
    response = requests.get(eventUrl + 'items', headers=headers, verify=False)
    productData = response.json()
    # pprint(productData)
    print('Found ' + str(productData['count']) + ' products')

    for product in productData['results']:
        # print('id ' + str(product['id']) + ' name ' + product['name']['de-informal'])
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
    print('Found ' + str(questionData['count']) + ' questions')

    for question in questionData['results']:
        # print('id ' + str(question['id']) + ' name ' + question['question']['de-informal'])
        questions[question['id']] = question
        if not question['options']:
            stats['answers'][question['id']] = 0
        else:
            for option in question['options']:
                # print('    id ' + str(option['id']) + ' name ' + option['answer']['de-informal'])

                if not (question['id'] in stats['answers']):
                    stats['answers'][question['id']] = {}
                    strData['question'][question['id']] = {}

                stats['answers'][question['id']][option['id']] = 0
                strData['question'][question['id']][option['id']] = option['answer']['de-informal']

    """ Quotas """
    response = requests.get(eventUrl + 'quotas', headers=headers, verify=False)
    quotaData = response.json()
    # pprint(quotaData)
    print('Found ' + str(quotaData['count']) + ' quotas')
    for quota in quotaData['results']:
        for productId in quota['items']:
            quotas[productId] = quota


def syncUserData():
    global eventDate

    print('Sync User Data')
    """ Orders """
    numberOfRegistration = 0
    orderUrl = eventUrl + 'orders'
    while True:
        for timeout in range(0, 10):
            response = requests.get(orderUrl, headers=headers, verify=False)
            if response.status_code == 200:
                break

        orderData = response.json()
        print('.')  # print('.', end='', flush=True)

        # Order Status
        # n – pending
        # p – paid
        # e – expired
        # c – canceled
        # r – refunded

        for order in orderData['results']:

            if (order['status'] != 'c') and (order['status'] != 'r'):
                numberOfRegistration += 1
                user = {}
                user[u'Name'] = ''
                user[u'Auch wenn ich das ganze Wochenende gebucht habe, übernachte ich nicht im Connect-Quartier.'] = 'False'
                user[u'E-Mail'] = order['email']
                secret = ''

                for position in order['positions']:
                    if position['attendee_name'] is not None:
                        user[u'Name'] = position['attendee_name']

                    user[categories[products[position['item']]['category']]['name']['de-informal']] = \
                        products[position['item']]['name']['de-informal']

                    if position['variation'] is not None:
                        user[categories[products[position['item']]['category']]['name']['de-informal']] += ' ' + \
                            variations[position['item']][position['variation']]['value']['de-informal']

                    for answers in position['answers']:
                        user[questions[answers['question']]['question']['de-informal']] = answers['answer']

                    if secret == '':
                        secret = position['secret']

                if u'Geburtsdatum' in user:
                    dt = parser.parse(user[u'Geburtsdatum'])
                    age = dateutil.relativedelta.relativedelta(eventDate.date(), dt.date())
                    user[u'Alter'] = age.years

                user['order'] = position['order']

                stats['users'][secret] = user

        if orderData['next']:
            orderUrl = orderData['next']
        else:
            break

    print("\nFound " + str(numberOfRegistration) + " User")


def getEventName():
    return eventName

def findUser(qr):
    if not qr in stats['users']:
        syncUserData()

    if qr in stats['users']:
        return stats['users'][qr]
    else:
        return False


if __name__ == "__main__":
    syncEvents()
    syncEventData()
    pprint(findUser("ed84kp4agjy255jr2ftwphrm638znbwv"))

    exit()
