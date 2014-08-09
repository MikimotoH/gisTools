#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import dist_latlng
import codecs
import google_geocode
import sys
import os
import time
import json

dist = lambda g1,g2: dist_latlng.dist_latlng(g1[0],g1[1], g2[0], g2[1])
geocode = google_geocode.geocode
validStr = lambda s: s != None and len(s.strip())>0
base_radius = 1.5 # kilometer
g_geoDict_fname = 'geoDict.json'

g_geoDict= {}
def save_geoDict():
    global g_geoDict
    with codecs.open(g_geoDict_fname, mode = 'w', encoding='UTF-8') as f:
        json.dump(g_geoDict, f, indent=4, ensure_ascii=False)

def load_geoDict():
    global g_geoDict
    if os.path.isfile(g_geoDict_fname):
        with open(g_geoDict_fname, 'r') as f:
            g_geoDict = json.load(f, encoding='UTF-8')
        # convert list of lists  => list of tuples
        for k,v in g_geoDict.items():
            g_geoDict[k] = [ tuple(x) for x in v] if v else v

def list_elemAt(ls, i):
    return ls[i] if len(ls)>i else None

g_ApiKeys = []
g_queryCount=0

def first_or_default(ls, predicate): 
    return list_elemAt(filter( predicate, ls), 0)

def process_route(fin,fout,numStats, reverse = False):
    radius = 1
    prevGeo = None

    lines = []
    for iStat in range(0, numStats):
        lines.append( fin.readline() )
    if reverse:
        lines.reverse()

    for iStat in range(0, numStats):
        line = lines[iStat]
        cols = filter( validStr, map(unicode.strip, line.split('\t')))
        if len(cols) < 2:
            lines[iStat] = line
            continue
        station = cols[0]
        curGeo = tuple( map( float, cols[2].split(','))) if len(cols)>=3 else None
        if not curGeo and iStat > 0 :
            global g_geoDict
            curGeo = g_geoDict.get(station, None)
            if not curGeo:
                global g_queryCount, g_ApiKeys
                curGeo, status = geocode( station, g_ApiKeys[g_queryCount % len(g_ApiKeys) ] ) 
                time.sleep(0.5)
                g_queryCount+=1
                g_geoDict[station] = curGeo
                save_geoDict()
            if not prevGeo or not curGeo:
                lines[iStat] = line
                radius += 1
                if curGeo and len(curGeo)>0:
                    prevGeo = curGeo[0]
                continue
            print (u'iStat=%d Station="%s" radius=%d, curGeo=%s'%(iStat, station, radius, curGeo))
            curGeo = first_or_default(curGeo, lambda g: dist(g, prevGeo)<radius*base_radius )
        if curGeo: 
            lines[iStat] = u"\t" + "%s\t%s\t%f,%f\n"%(station, cols[1], curGeo[0], curGeo[1])
            radius = 1
            prevGeo = curGeo
        else:
            lines[iStat] = u"\t" + "%s\t%s\t\n"%(station, cols[1])
            radius+=1
    if reverse:
        lines.reverse()
    for iStat in range(0, numStats):
        fout.write(lines[iStat])
        fout.flush()
                    

def process(fin, fout, reverse):
    line = fin.readline()
    prevGeo=None
    while validStr(line) :
        if not line.startswith('\t'):
            # bus name declaration
            busName, goStats, backStats = line.split('\t')

            goStats = int(goStats)
            backStats = int(backStats)
            fout.write(line)
            print(line.rstrip())
            process_route(fin,fout, goStats, reverse)
            process_route(fin,fout, backStats, reverse)
            line = fin.readline()
            continue


def main():
    finName = sys.argv[1] if len(sys.argv)>=2 else "all_buses_6.txt"
    foutName = os.path.splitext(finName)[0] + '_out' + '.txt'
    global g_ApiKeys
    
    with open("apikeys.json", mode="r") as f:
        g_ApiKeys = json.load(f, encoding='UTF-8')
    reverse = True
    load_geoDict()      
    with codecs.open(finName, mode='r', encoding='UTF-8') as fin, codecs.open(foutName, mode='w', encoding='UTF-8') as fout:
        process(fin, fout, reverse)

if __name__ == "__main__":
    main()

