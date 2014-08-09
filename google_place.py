#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import urllib
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import lxml
import random
from lxml import etree
from lxml.html import fromstring


def warning(msg):
    sys.stderr.write("Warning: %s\n" % msg)


def main():
    random.seed()
    lat, lng = map(float, sys.argv[1].split(','))
    with open('apikeys.json', mode='r') as f:
        apikeys = json.load(f, encoding='utf-8')

    apikey = apikeys[random.randrange(1, len(apikeys))]
    places_json = json.loads(str(urlopen('https://maps.googleapis.com/maps/api/place/nearbysearch/json?' + \
        'key={}&location={},{}'.format(apikey, lat, lng) + \
        '&rankby=distance&language=zh-TW&types=bus_station').readall(),'utf8'))

    if places_json['status'] != 'OK':
        warning("status=" + places_json['status'])
        return
    places_results = places_json['results']
    for result in places_results:
        placeid = result['place_id']
        detail = json.loads(str(urlopen('https://maps.googleapis.com/maps/api/place/details/' + \
            'json?key={}&placeid={}'.format(apikey,placeid) + \
            '&language=zh-TW').readall(), 'utf8'))
        url = detail['result']['url']
        req = Request(url, headers={'Accept-Language': 'zh-TW'})
        buspage = str(urlopen(req).readall(), 'big5')
        tree = lxml.html.document_fromstring(buspage)
        elm = tree.xpath("/html/body/div[1]/div/div[4]/div[4]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div[2]/div/table/tr/td")[0]
        bus_name = elm.text_content().strip()
        print("bus_name = %s"%bus_name)


if __name__ == "__main__":
    main()
