import json
from datetime import datetime
import bottle
from bottle import route, request, default_app, template, response
from beaker.middleware import SessionMiddleware
from dice import Dice2007
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

def validate_number(n):
    """Currently unused. This is a stub for number validation
    before passing values to the Dice2007 object."""
    try: float(n)
    except ValueError: raise Exception('Input needs to be a number.')
    else: return n

def do_session(request, newdice=False):
    """
    Checks for existence of session data. Writes variables as necessary.
    ...
    Keyword Arguments:
    newdice: obj
        A Dice2007 object.
    """
    s = request.environ.get('beaker.session')
    if newdice:
        dice = newdice
        s['dice'] = dice
    if 'dice' not in s: 
        dice = Dice2007()
        s['dice'] = dice
    return s

@route('/')
def index():
    """Returns index page."""
    do_session(request)
    return page()

@route('/<equations>')
def matlab(equations):
    """
    Create dice objects with equations sets based on URL. Then return web page.
    ...
    Args:
        equation (str): One of 'nordhaus', 'matlab', or 'docs'
    Returns:
        page()
    ...
    """
    dice = Dice2007(eq=equations)
    do_session(request, newdice=dice)
    return page()


def page():
    """
    Return HTML for all pages.
    ...
    Args:
        None
    Returns:
        HTML
    """
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
    """
    Get data from <form>, run DICE loop.
    ...
    Args:
        None
    Returns:
        Formatted step values
    """
    s = do_session(request)
    thisdice = s['dice']
    form = request.forms
    all_parameters = get_all_parameters()
    for p in all_parameters:
        try: all_parameters[p]['disabled']
        except (KeyError, AttributeError):
            try: a = getattr(thisdice, p)
            except AttributeError: pass
            else:
                try:
                    a.value = float(getattr(form, p))
                except ValueError: pass #print p, getattr(form, p)
    if form.treaty_switch == 'on':
        thisdice.treaty_switch.value = True
    else: thisdice.treaty_switch.value = False
    thisdice.loop()
    return thisdice.format_output()

@route('/csv', method='POST')
def csv_output():
    data = request.forms.data
    response.set_header('Content-Disposition', 'attachment; filename="WebDICE-Data.csv"')
    return data

app = SessionMiddleware(default_app(), session_opts)
application = app
