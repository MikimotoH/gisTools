#!/usr/bin/env python
# -*- coding : utf-8 -*-
import sys
import json
from urllib2 import quote, urlopen

def warning(msg):
    pass
    #sys.stderr.write( "Warning: %s\n"%msg )
    #print(u"WARNING: %s"% ustr, file=sys.stderr)

def geocode(addr):
    gurl = "http://maps.googleapis.com/maps/api/geocode/json?"+ \
            "sensor=false&language=zh-TW&region=tw&address=%s" \
            % quote(addr.decode('utf8').encode('utf8'))
    f = urlopen(gurl)
    s = f.read()
    x = json.loads(s)
    if x['status'] != 'OK':
        warning('status is "%s"' % x['status'])
        return None
    results = x['results']
    ret = []
    for i in range(0, len(results)):
        lat = results[i]['geometry']['location']['lat']
        lng = results[i]['geometry']['location']['lng']
        ret.append((lat,lng))
    return ret
    


def main():
    if len(sys.argv) < 2 :
        sys.stderr.write("parameter address must be input")
        return 1
    addr = sys.argv[1]
    ret = geocode(addr)
    if(ret == None):
        return 1
    for i in range(0, len(ret)):
        print("LatLng=%f,%f" % (ret[i][0], ret[i][1]))

if __name__ == "__main__":
    main()
