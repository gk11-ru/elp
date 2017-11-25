# -*- coding: utf-8 -*-

import json, urllib2, base64

from api import mydict, hsh, accept_msg
from api.fo import file_to_obj, lst, gm

URL='http://gk11.ru/u/'
ECHOES=['gk11.ru', 'openbsd.talk', 'std.prog','std.tech', 'std.club', 'std.game', 'std.bugs']

def getf(l):
    print 'fetch %s' % l
    from StringIO import StringIO
    import gzip
    request = urllib2.Request(l)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)
    if response.info().get('Content-Encoding') == 'gzip':
        f = gzip.GzipFile(fileobj=StringIO( response.read()))
    else:
        f = response
    return f.read()

def sep(l,step=50):
    for x in range(0,len(l),step):
        yield l[x:x+step]

def unp(s):
    return base64.b64decode(s.replace('-','+').replace('_','/'))

def walk_el(out):
    ea = ''; el = {}
    for n in out.splitlines():
        if '.' in n:
            ea = n
            el[ea] = []
        elif ea:
            el[ea].append(n)
    return el


def parse():
    out = getf('%se/%s' % (URL, '/'.join(ECHOES)))
    el = walk_el(out)
    for ea in ECHOES:
        topics, msgdb, tails = {}, {}, []
        myel = lst('e/' + ea)
        print 'analyze echo...'
        for x in myel:
            msgdb[x] = file_to_obj(gm(x))
            msgdb[x].msgid = x
            topics[x] = msgdb[x].topicid
        print 'download...'
        dllist = [x for x in el[ea] if x not in myel]
        for dl in sep(dllist):
            s = getf('%sm/%s' % (URL, '/'.join(dl)))
            for n in s.splitlines():
                msgid,kod = n.split(':',1)
                msgdb[msgid] = file_to_obj(unp(kod).decode('utf-8'))
                msgdb[msgid].msgid = msgid

        for dl in dllist:
            if not msgdb[dl].repto:
                msgdb[dl].topicid = dl
                topics[msgid] = dl
            else:
                if msgdb[dl].repto in topics:
                    msgdb[dl].topicid = topics[msgdb[dl].repto]
                    topics[dl] = msgdb[dl].topicid
                else:
                    if not msgdb[dl].topicid:
                        tails.append(dl)

        print 'find tails...'
        for x in tails:
            myway, xx, iid = [], x, ''
            while True:
                myway.append(xx)
                xx = msgdb[xx].repto
                if not xx in msgdb:
                    break
                if msgdb[xx].topicid:
                    iid = msgdb[xx].topicid
                    break
                if not msgdb[xx].repto:
                    iid = xx
                    break
            if iid:
                for xx in myway:
                    msgdb[xx].topicid = iid

        for x in dllist:
            if not msgdb[x].topicid:
                print x,
            else:
                accept_msg(msgdb[x])

parse()
