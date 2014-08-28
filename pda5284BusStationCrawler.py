#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import lxml
from lxml import html
from urllib.request import urlopen, Request
from urllib.parse import quote
from collections import OrderedDict


def warning(msg):
    sys.stderr.write("Warning: %s\n" % msg)


def get_webpage(url):
    req = Request(url)
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


def crawl_stations(bus):
    busInfo2 = get_webpage("http://pda.5284.com.tw/MQS/businfo2.jsp?routename="+quote(bus))
    tree = html.document_fromstring(busInfo2)
    table = tree.xpath("/html/body/center/table/tr[5]/td/table")[0]
    nColumns = len(table.getchildren())
    stations_go = []
    stations_back = []
    nRows = len(table.xpath("tr[{}]/td[1]/table".format(nColumns))[0].getchildren())
    for s in range(1, nRows+1):
        try:
            node = table.xpath("tr[{}]/td[1]/table/tr[{}]/td[1]".format(nColumns, s))[0]
        except:
            import pdb; pdb.set_trace()
            break
        stations_go.append(node.text_content().strip())
    if nColumns == 1:
        return (stations_go, [])
    nRows = len(table.xpath("tr[{}]/td[2]/table".format(nColumns))[0].getchildren())
    for s in range(1, nRows+1):
        try:
            node = table.xpath("tr[{}]/td[2]/table/tr[{}]/td[1]".format(nColumns, s))[0]
        except:
            break
        stations_back.append(node.text_content().strip())
    return (stations_go, stations_back)


def crawl_all_routes():
    busInfo1 = get_webpage("http://pda.5284.com.tw/MQS/businfo1.jsp")
    tree = lxml.html.document_fromstring(busInfo1)
    busNames = []
    for i in range(5, 15):
        node = tree.xpath("/html/body/center/table[1]/tr[{0}]/td/select/option".format(i));
        buses = list(map(lambda n: n.text_content().strip(), node))[1:]
        busNames += buses

    # remove duplicate bus names
    return list(OrderedDict.fromkeys(busNames))


def crawl_all_bus_stations():
    busNames = crawl_all_routes()
    for bus in busNames:
        yield (bus, crawl_stations(bus))


field_sep = " "*3


def crawl_write_bus_stations(fileName):
    fileTitle, _ = os.path.splitext(fileName)
    with open(fileName, mode='w') as fout:
        import pdb; pdb.set_trace()  # XXX BREAKPOINT
        for bus, (stations_go, stations_back) in crawl_all_bus_stations():
            fout.write("{}\t{}\t{}\n".format(bus,len(stations_go),len(stations_back)))
            fout.write(field_sep + field_sep.join(stations_go)+"\n")
            fout.write(field_sep + field_sep.join(stations_back)+"\n")
            fout.flush()

    #with open(fileTitle+'.json', mode='w') as fout:
        #json.dump(busStations, fout, ensure_ascii=False, indent=4)


def validStr(s):
    return s and len(s.strip())>0


def load_all_bus_stations(fileName):
    with open(fileName, mode='r') as fin:
        triplet = []
        for line in fin:
            if line.startswith(field_sep):
                stations = list(filter(validStr, map(str.strip, line.split(field_sep))))
                triplet.append(stations)
            else:
                triplet.append(line.split('\t')[0])
            if len(triplet) == 3:
                yield tuple(triplet)
                triplet = []


def recrawl_bus_with_empty_station():
    fileName = sys.argv[1] if len(sys.argv) > 1 else 'all_bus_stations.txt'
    foutName, _ = os.path.splitext(fileName)
    foutName += '_out.txt'
    with open(foutName, mode='w') as fout:
        for bus, stations_go, stations_back in load_all_bus_stations(fileName):
            if len(stations_go) == 0:
                stations_go, stations_back = crawl_stations(bus)
            fout.write('{}\t{}\t{}\n'.format(bus, len(stations_go), len(stations_back)))
            fout.write(field_sep + field_sep.join(stations_go)+'\n')
            fout.write(field_sep + field_sep.join(stations_back)+'\n')
            fout.flush()


def main():
    recrawl_bus_with_empty_station()


if __name__ == '__main__':
    main()
