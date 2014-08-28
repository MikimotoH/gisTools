#!/usr/bin/env python3
# -*- coding: utf8 -*-
from os import path
import json
from google_place import get_web_json

kasper_stop_url='http://api.taipeibus.kasper.com.tw/?url=http://imp.5284.com.tw:3621/TaipeiBusService/Stop.aspx?DataFormat=json'
kasper_route_url='http://api.taipeibus.kasper.com.tw/?url=http://imp.5284.com.tw:3621/TaipeiBusService/Route.aspx?DataFormat=json'

field_sep=' '*3
go=0
back=1

def load_all_bus_stations(fileName):
    triplet = []
    with open('all_bus_stations.txt', mode='r') as fin:
        for line in fin:
            if not line.startswith(field_sep):
                triplet.append( line.split('\t')[0] )
            else:
                stations = [ x.strip() for x in line.split(field_sep) if x.strip() ]
                triplet.append(stations)
                if len(triplet) == 3:
                    yield tuple(triplet)
                    triplet = []



def xstr(s):
    return s if s else ''


def similar_station(curSt, prevSt, stop_json, routesDict):
    stops = [x for x in stop_json if x['nameZh'] == curSt]
    if prevSt:
        for st in stops:
            routeId = int(st['routeId'])
            prevStops = [x for x in stop_json if x['nameZh'] == prevSt and int(x['routeId'])==routeId]
            if prevStops:
                return st
    if stops:
        return stops[0]
    return None


def main():
    if path.isfile('kasper_stop.json'):
        with open('kasper_stop.json', mode='r') as fin:
            stop_json = json.load(fin, encoding='utf8')
    else:
        stop_json = get_web_json(kasper_stop_url)
    if path.isfile('kasper_route.json'):
        with open('kasper_route.json', mode='r') as fin:
            route_json = json.load(fin, encoding='utf8')
    else:
        route_json = get_web_json(kasper_route_url)

    stop_json = stop_json['BusInfo']
    route_json = route_json['BusInfo']

    # load all_bus_stations.txt
    all_bus_stations = list(load_all_bus_stations('all_bus_stations.txt'))
    routes = [ (x['nameZh'], int(x['Id'])) for x in route_json]
    routesDict = dict(routes)

    with open('stations_latlng.txt', mode='w') as fout:
        for bus, stations_go, stations_back in all_bus_stations:
            routeId = routesDict.get(bus)
            fout.write('{}\t{}\t{}'.format(bus, len(stations_go), len(stations_back)))
            if routeId:
                fout.write('\n')
            else:
                fout.write('\t#guess\n')
            fout.flush()

            stations = stations_go + stations_back
            if routeId:
                stops = sorted([x for x in stop_json if int(x['routeId'])==routeId ], key=lambda x: (x['goBack'],x['seqNo']))

            for index,curSt in enumerate(stations):
                curDir=go if index < len(stations_go) else back
                if index>0:
                    prevDir=go if index-1 < len(stations_go) else back
                    prevSt = stations[index-1] if index>0 else ''
                    if prevDir != curDir:
                        prevSt = ''
                else:
                    prevSt=''
                    prevDir=None

                if routeId:
                    loc = [x for x in stops if x['nameZh']==curSt and int(x['goBack'])==curDir]
                    if loc:
                        loc = (loc[0]['latitude'], loc[0]['longitude'])
                    else:
                        loc = [ x for x in stops if x['nameZh']==curSt]
                        if loc:
                            loc = (loc[0]['latitude'], loc[0]['longitude'])
                        else:
                            loc=(None,None)
                else:
                    loc = similar_station(curSt, prevSt, stop_json, routesDict)
                    if loc:
                        loc = (loc['latitude'], loc['longitude'])
                    else:
                        loc = (None,None)

                fout.write('\t{}\t{}\t{}\n'.format(curSt, xstr(loc[0]), xstr(loc[1])))
                fout.flush()


if __name__ == '__main__':
    main()
