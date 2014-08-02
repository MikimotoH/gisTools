#!/usr/bin/env python
# -*- coding : utf-8 -*-
import sys
import json
import urllib2

def geocode(addr):
    gurl = "http://maps.googleapis.com/maps/api/geocode/json?"+ \
            "sensor=false&language=zh-TW&region=tw&address=%s" \
            %(urllib2.quote(addr.decode('utf8').encode('utf8')))
    f = urllib2.urlopen(gurl)
    s = f.read()
    x = json.loads(s)
    lat = x['results'][0]['geometry']['location']['lat']
    lng = x['results'][0]['geometry']['location']['lng']
    return (lat,lng)
    


def main():
    addr = sys.argv[1]
    res = geocode(addr)
    print("LatLng=%f,%f" % (res[0], res[1]))

if __name__ == "__main__":
    main()
