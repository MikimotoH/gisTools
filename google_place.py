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


def dump_list(ls):
    return '[' + ','.join(ls) + ']'


def get_webpage(url):
    """ Given a HTTP/HTTPS url and then returns string
    Returns:
        string of HTML source code
    """
    req = Request(url, headers={'Accept-Charset': 'utf-8',
                                'Accept-Language': 'zh-tw,en-us;q=0.5'})
    with urlopen(req) as rsq:
        _, _, charset = rsq.headers['Content-Type'].partition('charset=')
        if not charset:
            charset = 'utf-8'
        htmlbytes = rsq.readall()
    charset = charset.strip()
    try:
        return str(htmlbytes, charset)
    except (UnicodeDecodeError):
        warning('encoding htmlbytes to {} failed'.format(charset))
        with open('UnicodeDecodeError.html', 'wb') as fout:
            fout.write(htmlbytes)
        raise


def get_web_json(url):
    with urlopen(url) as rsq:
        return json.loads(str(rsq.readall(), 'utf8'))


def nearby_bus_stations(lat, lng, apikey=""):
    """ Return a list of nearby bus stations around the location
    Args:
        lat: (float) latitude in degrees
        lng: (float) longitude in degrees
        apikey: Google API Key which enables Place API
    Yields:
        tuple(station:str, latitude: float, longitude: float, list[bus: string])
    Example:
        >>> sts = list(nearby_bus_stations(25.021072,121.551788))
        >>> print sts[0]
        ("黎明社教中心", 25.019798, 121.551818, ["懷恩專車S32"])
    """
    places = get_web_json(
        'https://maps.googleapis.com/maps/api/place/nearbysearch/json?' +
        'key=%s&location=%f,%f' % (apikey, lat, lng) +
        '&rankby=distance&language=zh-TW&types=bus_station')
    if places['status'] == 'OK':
        for result in places['results']:
            placeid = result['place_id']
            detail = get_web_json(
                'https://maps.googleapis.com/maps/api/place/details/' +
                'json?key=%s&placeid=%s' % (apikey, placeid) +
                '&language=zh-TW')
            station = detail['result']['name']
            loc = detail['result']['geometry']['location']

            try:
                buspage = get_webpage(detail['result']['url'])
            except:
                continue
            tree = lxml.html.document_fromstring(buspage)
            try:
                bus_elm = tree.xpath("/html/body/div[1]/div/div[4]/div[4]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div[2]/div/table/tr/td")[0]
            except (IndexError):
                warning('xpath get bus failed')
                with open('IndexError.html', 'w') as fout:
                    fout.write(buspage)
                continue
            buses = list(filter(lambda s: len(s.strip()) > 0,
                                bus_elm.text_content().strip().split()))
            yield (station, float(loc['lat']), float(loc['lng']), buses)
    else:
        warning("status=" + places['status'])


def main():
    random.seed()
    lat, lng = map(float, sys.argv[1].split(','))
    with open('apikeys.json', mode='r') as f:
        apikeys = json.load(f)
    apikey = apikeys[random.randrange(1, len(apikeys))]
    for st, st_lat, st_lng, buses in nearby_bus_stations(lat, lng, apikey):
        print('Station: "{}", ({},{}), Buses={}'.format(
            st, st_lat, st_lng, dump_list(buses)))


if __name__ == "__main__":
    main()
