import json
from datetime import datetime
from flask import Flask
from flask import render_template, request, make_response
from flask_beaker import BeakerSession
from webdice.dice import Dice2007
from conf.web import get_measurements, paragraphs_html
from conf.web import get_all_parameters, get_advanced_tabs, get_basic_tabs

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
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    return render_template(
        'index.html',
        now=now,
        paragraphs_html=paragraphs_html('index'),
    )

@app.route('/advanced')
def advanced():
    do_session(request)
    tabs = get_advanced_tabs()
    return page(tabs, 'advanced')

@app.route('/basic')
def basic():
    do_session(request)
    tabs = get_basic_tabs()
    return page(tabs, 'basic')


def page(tabs, tpl='index'):
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
    all_parameters = get_all_parameters()
    without_sections = []
    for s in measurements:
        for m in s['options']:
            without_sections.append(m)
    graph_locations = ['topleft', 'topright', 'bottomleft', 'bottomright', ]
    graph_names = ['essential', 'climate', 'economy', ]
    m = json.JSONEncoder().encode(without_sections)
    graph_locations = json.JSONEncoder().encode(graph_locations)
    graph_names = json.JSONEncoder().encode(graph_names)
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    return render_template(
        tpl + '.html',
        measurements=m,
        graph_locations=graph_locations,
        graph_names=graph_names,
        tabs=tabs,
        dropdowns=measurements,
        paragraphs_html=paragraphs_html(tpl),
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
    this_dice = s['dice']
    form = request.form
    all_parameters = get_all_parameters()
    for p in all_parameters:
        try:
            p['disabled']
        except (KeyError, AttributeError):
            try:
                getattr(this_dice, p['machine_name'])
            except AttributeError:
                pass
            else:
                try:
                    this_dice.__dict__[p['machine_name']] = float(form[p['machine_name']])
                except (ValueError, AttributeError, KeyError):
                    pass
    try:
        this_dice.damages_model = form['damages_model']
    except KeyError:
        pass
    policy = form['policy_type']
    this_dice.treaty = False
    this_dice.carbon_tax = False
    if policy == 'treaty':
        this_dice.treaty = True
    elif policy == 'optimized':
        this_dice.optimize = True
    elif policy == 'carbon_tax':
        this_dice.carbon_tax = True
    this_dice.loop()
    this_dice.optimize = False
    return this_dice.format_output()

@app.route('/csv', methods=['POST',])
def csv_output():
    data = request.form['data']
    response =  make_response(data)
    response.headers['Content-Disposition'] = 'attachment; filename="WebDICE-Data.csv"'
    return response

if __name__ == '__main__':
    app.run()