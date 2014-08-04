#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import dist_latlng
import codecs
import google_geocode

dist = lambda g1,g2: dist_latlng.dist_latlng(g1[0],g1[1], g2[0], g2[1])
geocode = google_geocode.geocode
validStr = lambda s: s != None and len(s)>0


def main():
    with open('red13.txt', 'r') as fin, open('red13_out.txt', 'w') as fout:
        line = fin.readline()
        prevGeo=None
        base_radius = 1.5 # kilometer
        radius = base_radius
        while validStr(line) :
            if not line.startswith('\t'):
                # bus name declaration
                fout.write(line)
                line = fin.readline()
                continue
            cols = filter( validStr, map(str.strip, line.split('\t')))
            if cols[0] == '慈濟志業中心':
                import pdb; pdb.set_trace()
            if len(cols) == 3:
                curGeo = tuple( map( float, cols[2].split(',')))
            else:
                curGeo = geocode( cols[0] )
                if not prevGeo or not curGeo:
                    fout.write(line)
                    radius += base_radius
                    line = fin.readline()
                    prevGeo = curGeo[0] if len(curGeo)>0 else None
                    continue
                print ('stat="%s", radius=%f'%(cols[0], radius))
                nearGeo = filter( lambda g: dist(g, prevGeo)<radius, curGeo)
                curGeo = nearGeo[0] if nearGeo else None
            if curGeo: 
                fout.write("\t" + "%s\t%s\t%f,%f\n"%(cols[0], cols[1], curGeo[0], curGeo[1]) )
                radius = base_radius
            else:
                fout.write("\t" + "%s\t%s\t\n"%(cols[0], cols[1]) )
                radius += base_radius
            prevGeo = curGeo
            line = fin.readline()

if __name__ == "__main__":
    main()
