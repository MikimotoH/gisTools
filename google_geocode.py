#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import sys
import json
from urllib.request import urlopen
from urllib.parse import urlencode


def warning(msg):
    sys.stderr.write("Warning: %s\n" % msg)


def get_web_json(url):
    with urlopen(url) as rsq:
        return json.loads(str(rsq.readall(), 'utf8'))


def geocode(addr, apiKey=""):
    params = [
        ('sensor', 'false'),
        ('language', 'zh-TW'),
        ('region', 'tw'),
        ('address', addr),
    ]
    if apiKey:
        params.append('key', apiKey)

    js = get_web_json('https://maps.googleapis.com/maps/api/geocode/json?' +
                      urlencode(params))
    status = js['status']
    if status != 'OK':
        raise Exception(str(status))
    for res in js['results']:
        lat = res['geometry']['location']['lat']
        lng = res['geometry']['location']['lng']
        yield (lat, lng)


def intersects(list1, list2):
    """Returns True if list1 intersects with list2; otherwise False"""
    return not set(list1).isdisjoint(set(list2))


def get_intersection(list1, list2):
    return list(set(list1) & set(list2))


def reverse_geocode(lat, lng, apiKey=''):
    """return (postal_code) (country) State City District Village Street number
        as well as formatted_address using google API
    """
    params = [
        ('sensor', 'false'),
        ('language', 'zh-TW'),
        ('region', 'tw'),
        ('latlng', str(lat)+','+str(lng)),
    ]
    if apiKey:
        params.append('key', apiKey)
    js = get_web_json('https://maps.googleapis.com/maps/api/geocode/json?' +
                      urlencode(params))
    status = js['status']
    if status != 'OK':
        raise status
    result = js['results'][0]
    comps = result['address_components'][:]
    comps.reverse()
    adm_types = ['postal_code', 'country', 'administrative_area_level_2',
                 'locality', 'sublocality', 'route', 'street_number']
    comps = list(filter(lambda t: t[1], map(
        lambda d: (d['long_name'], get_intersection(d['types'], adm_types)[0]), comps)))
    return {'formatted_address': result['formatted_address'],
            'address_components': comps}


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("parameter address must be input")
        return 1
    addr = sys.argv[1]
    lat, lng = None, None
    try:
        lat, lng = list(map(float, addr.split(',')))
    except:
        pass

    apiKey = sys.argv[2] if len(sys.argv) > 2 else ""

    try:
        if lat:
            ret = reverse_geocode(lat, lng, apiKey)
            print(ret['formatted_address'])
        else:
            for ret in geocode(addr, apiKey):
                print("LatLng=%f,%f" % (ret[0], ret[1]))
    except str as status:
        warning('status is "%s"' % str(status))


if __name__ == "__main__":
    main()
