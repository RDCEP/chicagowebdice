import json
from datetime import datetime
from flask import Flask
from flask import render_template, request, make_response
from flask_beaker import BeakerSession
from dice import Dice2007
from conf import parse_conf, get_measurements, paragraphs_html
from conf import get_all_parameters

session_opts = {
    'session.type': 'ext:memcached',
    'session.cookie_expires': True,
    'session.lock_dir': './data',
    'session.url': '127.0.0.1:11211',
    'session.memcache_module': 'pylibmc',
    'session.auto': True
}

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'Ad78gii#$3979oklaklf'
BeakerSession(app)

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

@app.route('/')
def index():
    """Returns index page."""
    do_session(request)
    return page()

@app.route('/advanced')
def advanced():
    do_session(request)
    return page('advanced')

@app.route('/basic')
def basic():
    do_session(request)
    return page('basic')


def page(t='index'):
    """
    Return HTML for all pages.
    ...
    Args:
        None
    Returns:
        HTML
    """
    measurements = get_measurements()
    # tabs = get_tabs()
    these_tabs, all_parameters = parse_conf()
    without_sections = []
    for s in measurements:
        for m in s['options']:
            without_sections.append(m)
    graph_locations = ['topleft', 'topright', 'bottomleft', 'bottomright']
    m = json.JSONEncoder().encode(without_sections)
    g = json.JSONEncoder().encode(graph_locations)
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    return render_template(
        t + '.html',
        measurements=m,
        graph_locations=g,
        tabs=these_tabs,
        dropdowns=measurements,
        paragraphs_html=paragraphs_html(t),
        all_parameters=all_parameters,
        now=now,
    )

@app.route('/run', methods=['POST',])
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
    form = request.form
    print form['dela']
    all_parameters = get_all_parameters()
    for p in all_parameters:
        try: all_parameters[p]['disabled']
        except (KeyError, AttributeError):
            try: a = getattr(thisdice, p)
            except AttributeError: pass  #print a, p
            else:
                try:
                    a.value = float(form[p])
                except (ValueError, AttributeError): pass  #print p, getattr(form, p)
    thisdice.damages_model.value = form['damages_model']
    policy = form['policy_type']
    thisdice.treaty = False
    thisdice.carbon_tax = False
    if policy == 'treaty':
        thisdice.treaty = True
    elif policy == 'optimized':
        thisdice.optimize = True
    elif policy == 'carbon_tax':
        thisdice.carbon_tax = True
    thisdice.loop()
    thisdice.optimize = False
    return thisdice.format_output()

@app.route('/csv', methods=['POST',])
def csv_output():
    data = request.form['data']
    response =  make_response(data)
    response.headers['Content-Disposition'] = 'attachment; filename="WebDICE-Data.csv"'
    return response

if __name__ == '__main__':
    app.run()