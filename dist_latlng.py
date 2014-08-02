#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import sys

sq = lambda x: x*x

def dist_latlng(lat1, lon1, lat2, lon2):
    """
    lat: latitude in degrees
    lng: longitude in degrees
    """
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = sq(math.sin(dphi/2)) + math.cos(phi1)*math.cos(phi2) * sq(math.sin(dlmb/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R*c

def main():
    if len(sys.argv) != 3:
        print("error: arguments must be two. Latitude/Longitude are separated by comma.\n"
        +"e.g. %s 25.155890,121.408600 25.1568419,121.405074" % sys.argv[0])
        sys.exit()
    ll1 = sys.argv[1].split(",")
    ll2 = sys.argv[2].split(",")
    dist = dist_latlng(float(ll1[0]), float(ll1[1]), float(ll2[0]), float(ll2[1]))
    print ("dist=%f km"%dist)

if __name__ == "__main__":
    main()

