# -*- coding: utf-8 -*-

import api
from api.sx import mydict, gts, hsh, b64c, b64d
from api.bottle import route, run, request, response, template, static_file, post, redirect, HTTPError
from api.regdata import udata

def u():
    return udata(request.cookies.kvitok.encode('utf-8'))

@route('/')
def redir_page():
    redirect('/start')

@route('/start')
def start_page():
    mo = [x.split()[0] for x in reversed(api.lst('m.accepted'))]
    return template('start.html',out=api.forums_list(),mo=mo,u=u())

@route('/favicon.ico')
def no_favicon():
    raise HTTPError(404)

@route('/<raw:re:e|m>/<oid>')
def raw_file(raw,oid):
    response.content_type = 'text/plain; charset=utf-8'
    return api.rf('data/%s/%s' % (raw,oid))

@route('/u/e/<f:path>')
def echo_bundle(f):
    response.content_type = 'text/plain; charset=utf-8'
    out = []
    for n in [x for x in f.split('/') if '.' in x]:
        out.append(n)
        out += [x for x in api.lst('e/%s' % n)]
    return '\n'.join(out)

@route('/u/all')
def all_bundle():
    response.content_type = 'text/plain; charset=utf-8'
    out = ''
    el, fl = {}, api.lst('e.list')
    for ea in fl:
        el[ea] = api.lst('e/%s' % ea)
    for n in [x.split()[0] for x in api.lst('m.accepted')]:
        for ea in fl:
            if n in el[ea]:
                out += '%s:%s\n' % (n,ea)
                break
    return out

@route('/u/m/<f:path>')
def msg_bundle(f):
    response.content_type = 'text/plain; charset=utf-8'
    return '\n'.join(['%s:%s' % (n, b64c(api.gm(n))) for n in f.split('/')]) + '\n'

@route('/list.txt')
def list_txt():
    out = ''
    response.content_type = 'text/plain; charset=utf-8'
    for n in api.echolist():
        out += '%s:%s:%s\n' % (n, len(api.lst('e/%s' % n)), api.echo_desc(n) or 'no desc')
    return out

@route(['/forum/<ea>', '/forum', '/forum/'])
def forum_list(ea=''):
    if not ea:
        ea = api.echolist()[0]
    pge = request.query.page or '1'
    return template('forum-list.html',out=api.forum_list(ea),ea=ea,u=u(),pge=int(pge)-1)

@route('/topic/<topicid>')
def topic_list(topicid):
    topic = api.lst('topic/%s' % topicid)
    msgs = mydict({n:api.get_msg(n) for n in topic[5:]})
    return template('forum-topic.html',topicid=topicid,topic=topic,msgs=msgs,u=u())

@route(['/blog/<ea>','/blog', '/blog/'])
def blog_list(ea=''):
    if not ea:
        ea = api.echolist()[0]
    blogs = api.lst('et/%s' % ea)
    comms = mydict({n:len(api.lst('topic/%s' % n))-6 for n in blogs})
    msgs = mydict({n:api.get_msg(n) for n in blogs})
    pge = request.query.page or '1'
    return template ('blog-list.html',ea=ea,blogs=blogs,msgs=msgs,comms=comms,pge=int(pge)-1)

@route('/msg/<topicid>')
def blog_topic(topicid):
    topic = api.lst('topic/%s' % topicid)
    mo = [api.get_msg(n) for n in topic[5:]]
    return template ('blog-topic.html',mo=mo)

@route('/tag/<tag>')
def blog_tag(tag):
    blogs = api.lst('tags/%s' % hsh(b64d(tag)))
    comms = mydict({n:len(api.lst('topic/%s' % n))-6 for n in blogs})
    msgs = mydict({n:api.get_msg(n) for n in blogs})
    return template ('blog-list.html',blogs=blogs,msgs=msgs,comms=comms,tag=tag)

@route('/echo/<ea>')
def echo_list(ea):
    mo = [n for n in reversed(api.lst('e/%s' % ea))]
    pge = request.query.page or '1'
    return template('echoarea.html',mo=mo,title=ea,ea=ea,u=u(),desc=api.echo_desc(ea),pge=int(pge)-1)

@route('/carbon/<carbon>/<uname:path>')
def carbon_copy(carbon,uname):
    mo = [n for n in reversed(api.lst('carbon/%s' % carbon))]
    if carbon.startswith('_'):
        title = 'Сообщения от пользователя %s' % uname
    else:
        title = 'Сообщения для пользователя %s' % uname
    return template('echoarea.html',mo=mo,title=title,u=u(),desc='Карбонки',ea='',pge=0)

@route('/lenta')
def lenta_list():
    mo = [n.split()[0] for n in reversed(api.lst('m.accepted'))]
    return template('echoarea.html',mo=mo,title='Лента сообщений',u=u(),ea='',desc='все сообщения всех эх',pge=0)

@route('/q/<ml_:path>')
def msg_list(ml_):
    ml = ml_.strip('/').split('/')
    mo = [n.split()[0] for n in ml]
    return template('echoarea.html',mo=mo,desc='',u=u(),ea='',title='Сообщения' if len(ml) > 1 else ml[0],pge=-1)


@route('/new/<typ>/<ea>/<topicid>/<repto>')
def reply_form(typ,ea,topicid,repto):
    if repto and repto != '-':
        prev = api.get_msg(repto)
    else:
        prev = mydict()
    return template('mform.html',u=u(),prev=prev,typ=typ,ea=ea,topicid=topicid,repto=repto)

@post('/new')
def create_message():
    ud = udata(request.forms.kvitok.encode('utf-8'))
    if not ud.check() or not ud.uname:
        return u'доступ не подтверждён, сочувствуем'
    nmsg = api.create_msg(request.forms,ud)
    if request.forms.typ == 'echo':
        redirect ('/echo/%s#go_%s' % (request.forms.ea, nmsg))
    else:
        redirect ('/%s/%s#go_%s' % (dict(forum='topic',blog='msg').get(request.forms.typ),request.forms.topicid or nmsg, nmsg))

@post('/u/point')
def create_message_point():
    ud = udata(request.forms.pauth.encode('utf-8'))
    dta = b64d(request.forms.tmsg.encode('utf-8')).decode('utf-8').splitlines()
    repto, tags = '', ''
    if dta[4].startswith('@repto:'):
        repto = dta[4][7:]
        if len(repto) != 20:
            return 'wrong repto!'
        txt = '\n'.join(dta[5:])
    elif dta[4].startswith('@tags:'):
        tags = dta[4][6:]
        txt = '\n'.join(dta[5:])
    else:
        txt = '\n'.join(dta[4:])
    mo = mydict(ea=dta[0],txt=txt,repto=repto,tags=tags,to=dta[1],title=dta[2] or '***')
    if repto:
        mo.topicid = api.get_msg(repto).topicid
    if ud.check() and ud.uname:
        nmsg = api.create_msg(mo,ud)
    return 'msg ok:%s' % nmsg

@route('/js/<pge>')
def js_page(pge):
    response.content_type = 'application/javascript; charset=utf-8'
    if pge == 'lenta.js':
        mo = [api.get_msg(n.split()[0]) for n in reversed(api.lst('m.accepted'))]
        if request.query.lim:
            mo = mo[:int(request.query.lim)]
    return template('js.tpl',mo=mo,rq=request.query)

@post('/user/testkey')
def key_test_api():
    if udata(request.forms.kvitok).check():
        return 'ok'

@post('/user/auth')
def auth_user_bykey():
    ud = udata(request.forms.kvitok.encode('utf-8'))
    if request.forms.kvitok:
        if ud.check():
            response.set_cookie('kvitok', ud.kvitok, path='/', max_age=7776000)
            return template('''<html><head>
                    <meta http-equiv="refresh" content="3; {{redir}}" />
                    </head><body><p>Пользователь: <b>{{ud.uname}}</b></p>
                    <p>Адрес: <b>{{ud.uaddr}}</b></p>
                    <p>Авторизация принята. Осуществляется переход по адресу: <a href="{{redir}}">{{redir}}</a></p></body></html>''', 
                    ud=ud, redir=request.forms.redir.encode('utf-8').decode('base64') or '/')
        else:
            return template('{{ud.uname}}<br>{{ud.uaddr}}<br><br>Ключ не принят, сожалеем. Обратитесь к производителю.',ud=ud)
    else:
        response.set_cookie('kvitok', '', path='/', max_age=7776000)
        return template('<html><head><meta http-equiv="refresh" content="3; {{redir}}" /></head><body><p>Авторизация cнята. Осуществляется переход по адресу: <a href="{{redir}}">{{redir}}</a></p></body></html>', ud=ud, redir=request.forms.redir.encode('utf-8').decode('base64') or '/')


@route('/user/auth')
def kvitok_form():
    return '<form method="post"><input type="text" name="kvitok" placeholder="Ввести сюда квиток, вида :223432...многобуквоцифр..565542:" style="width:100%"><input type="submit" value="Ok"></form>'

@route('/user/me')
def user_info():
    return template('user.html',u=u())

@route('/s/<f:path>')
def send_file(f):
    return static_file(f, root='./s')


run(host='127.0.0.1',port=15555,debug=True)
