import json
from datetime import datetime
import bottle
from bottle import route, request, default_app, template
from beaker.middleware import SessionMiddleware
from dice import dice2007
from server.conf import *

bottle.TEMPLATE_PATH = ['../templates/',]

session_opts = {
    'session.type': 'ext:memcached',
    'session.cookie_expires': True,
    'session.lock_dir': './data',
    'session.url': '127.0.0.1:11211',
    'session.memcache_module': 'pylibmc',
    'session.auto': True
}

dice = dice2007()

def do_session(request):
    s = request.environ.get('beaker.session')
    if 'dice' not in s: s['dice'] = dice
    return s

@route('/')
def index():
#    print tabs_html()
    do_session(request)
    measurements = get_measurements()
    graph_locations = get_graph_locations()
    m = json.JSONEncoder().encode(measurements)
    g = json.JSONEncoder().encode(graph_locations)
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    tpl = template('index',
        measurements=m,
        graph_locations=g,
        tabs_html=tabs_html(),
        dropdowns=measurements_html(),
        paragraphs_html=paragraphs_html(),
        now=now,
    )
    return tpl

@route('/run', method='POST')
def graphs():
    s = do_session(request)
    dice = s['dice']
    form = request.forms
    all_parameters = get_all_parameters()
    for p in all_parameters:
        try: all_parameters[p]['disabled']
        except (KeyError, AttributeError):
            try: a = getattr(dice, p)
            except AttributeError: pass
            else:
                print p, float(getattr(form, p))
                setattr(dice, p, float(getattr(form, p)))
    dice.loop()
    return dice.format_output()

app = SessionMiddleware(default_app(), session_opts)
application = app
