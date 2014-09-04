#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from lxml import html
import random
import re
from urllib.request import urlopen, Request


def warning(msg):
    sys.stderr.write("Warning: %s\n" % msg)


def dump_list(ls):
    return '[' + ','.join(ls) + ']'


def get_webpage(url):
    """ Given a HTTP/HTTPS url and then returns string
    Returns:
        string of HTML source code
    """
    req = Request(url, headers={'Accept-Charset': 'utf-8', 'Accept-Language': 'zh-tw,en-us;q=0.5'})
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


def amend_bad_json(bad_json):
    return re.sub(r'(?<=[,{}])(\w+):', r'"\1":', bad_json)


def nearby_bus2rec(res_dict, href):
    htmls = get_webpage(href)
    htm = html.fromstring(htmls)
    cur_bus = htm.xpath("/html/body/div[1]/div/div[4]/div[4]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div[2]/div/table/tr/td")
    if not cur_bus:
        return
    res_buses = [x.strip() for x in cur_bus[0].text_content().strip().split() if x.strip()]
    ppmarkerjson = htm.xpath("/html/body/div[@id='main']/div[@id='inner']/div[@id='page']/div[4]/div[@id='wpanel']/div[@id='placepagepanel']/div/div[@id='pp-marker-json']")
    if not ppmarkerjson:
        return
    ppmarkerjson = ppmarkerjson[0].text_content()
    marker = json.loads(amend_bad_json(ppmarkerjson))

    cid = marker['cid']
    if cid in res_dict:
        return
    lat = marker['latlng']['lat']
    lng = marker['latlng']['lng']
    res_name = htm.xpath("/html/body/div[@id='main']/div[@id='inner']/div[@id='page']/div[4]/div[@id='wpanel']/div[@id='placepagepanel']/div[@id='pppanel']/div[@id='pp-maincol']/div[@id='pp-headline']/div[@id='pp-headline-details']/div[1]/span[1]/span")
    if not res_name:
        return
    res_name = res_name[0].text_content()
    print('cid={} {} {} station="{}"'.format(cid, lat, lng, res_name))
    res_dict[cid] = ((lat, lng), res_buses, res_name)

    ppnearby = htm.find_class('pp-nearby-transit')[0]
    for ngb in ppnearby.getchildren()[1:]:
        href = dict(ngb.find("a").items())['href']
        nearby_bus2rec(res_dict, "https://maps.google.com"+href)


def nearby_bus2(lat,lng,apikey):
    """ Don't iterate results from nearbysearch, use URL instead
    This will save the usage of apikey.
    Yieds:
        tuple(station:str, latitude: float, longitude: float, list[bus: str])
    """
    places = get_web_json(
        'https://maps.googleapis.com/maps/api/place/nearbysearch/json?' +
        'key=%s&location=%f,%f' % (apikey, lat, lng) +
        '&rankby=distance&language=zh-TW&types=bus_station')
    if places['status'] != 'OK':
        warning("status=" + places['status'])
        return
    results = places['results']
    res_dict = {}
    for result in results:
        placeid = result['place_id']
        detail = get_web_json(
            'https://maps.googleapis.com/maps/api/place/details/' +
            'json?key=%s&placeid=%s' % (apikey, placeid) +
            '&language=zh-TW')
        nearby_bus2rec(res_dict, detail['result']['url'])
    return res_dict


def main():
    random.seed()
    lat, lng = map(float, sys.argv[1].split(','))
    with open('apikeys.json', mode='r') as f:
        apikeys = json.load(f)
    apikey = apikeys[random.randrange(0, len(apikeys))]
    res_dict = nearby_bus2(lat, lng, apikey)
    for cid in res_dict:
        latlng, buses, name = res_dict[cid]
        print('cid:"{}", Station:"{}", ({},{}), Buses={}'.format(
                cid, name, latlng[0], latlng[1], dump_list(buses)))



if __name__ == "__main__":
    main()
