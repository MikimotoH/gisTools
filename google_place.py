#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
from urllib.request import urlopen, Request
import lxml
import lxml.html
import random


def warning(msg):
    sys.stderr.write("Warning: %s\n" % msg)


def main():
    random.seed()
    lat, lng = map(float, sys.argv[1].split(','))
    with open('apikeys.json', mode='r') as f:
        apikeys = json.load(f)

    apikey = apikeys[random.randrange(1, len(apikeys))]
    places = json.loads(str(urlopen('https://maps.googleapis.com/maps/api/place/nearbysearch/json?' + \
        'key={}&location={},{}'.format(apikey, lat, lng) + \
        '&rankby=distance&language=zh-TW&types=bus_station').readall(),'utf8'))

    if places['status'] != 'OK':
        warning("status=" + places['status'])
        return
    for result in places['results']:
        placeid = result['place_id']
        detail = json.loads(str(urlopen('https://maps.googleapis.com/maps/api/place/details/' + \
            'json?key={}&placeid={}'.format(apikey,placeid) + \
            '&language=zh-TW').readall(), 'utf8'))
        url = detail['result']['url']
        station = detail['result']['name']
        loc = detail['result']['geometry']['location']
        req = Request(url, headers={'Accept-Language': 'zh-TW'})
        buspage = str(urlopen(req).readall(), 'big5')
        tree = lxml.html.document_fromstring(buspage)
        elm = tree.xpath("/html/body/div[1]/div/div[4]/div[4]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div[2]/div/table/tr/td")[0]
        bus= elm.text_content().strip()
        print('station="{}",bus="{}",loc={},{}'.format(station, bus, loc['lat'], loc['lng']))


if __name__ == "__main__":
    main()
