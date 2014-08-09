#!/usr/bin/env python
# -*- coding : utf-8 -*-
import sys
import json
from urllib2 import quote, urlopen
from urllib import urlencode


def warning(msg):
    sys.stderr.write("Warning: %s\n" % msg)


def geocode(addr, apiKey=""):
    geocode_params = {
        'sensor': 'false',
        'language': 'zh-TW',
        'region': 'tw',
        'address': addr.encode('utf8')
    }
    if apiKey:
        geocode_params['key'] = apiKey

    import pdb; pdb.set_trace()  # XXX BREAKPOINT
    gurl = 'https://maps.googleapis.com/maps/api/geocode/json?' +\
        urlencode(geocode_params)
    #'?sensor=false&language=zh-TW&region=tw&address='
    #+ quote(addr.encode('utf8'))
    if apiKey:
        gurl += "&key=%s" % apiKey
    f = urlopen(gurl)
    s = f.read()
    x = json.loads(s)
    status = x['status']
    if status != 'OK':
        warning('status is "%s"' % status)
        return (None, status)
    results = x['results']
    ret = []
    for i in range(0, len(results)):
        lat = results[i]['geometry']['location']['lat']
        lng = results[i]['geometry']['location']['lng']
        ret.append((lat, lng))
    return (ret, status)


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("parameter address must be input")
        return 1
    addr = sys.argv[1].decode('utf8')
    apiKey = sys.argv[2] if len(sys.argv) > 2 else ""
    ret, status = geocode(addr, apiKey)
    if ret and len(ret) > 0:
        for i in range(0, len(ret)):
            print("LatLng=%f,%f" % (ret[i][0], ret[i][1]))
    else:
        print('status = "%s"' % status)
        return 1

if __name__ == "__main__":
    main()
