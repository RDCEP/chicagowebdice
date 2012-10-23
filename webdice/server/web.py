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

def process_vars(form, s):
    # Get data from AJAX
    # Check for updated wind capacity, update property, create new plot object
    foo = form.foo
    if form.get('cap_percentage'):
        pass

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

@route('/ajax', method='POST')
def graphs():
    do_session(request)
    form = request.form
    all_parameters = get_all_parameters()
    values = {}
    for machine_name, parameter in all_parameters:
        try: form[machine_name]
        except:
            if parameter['is_range_control']:
                value = parameter['default']
            else: value = None
        else: value = form[machine_name]
        if parameter['is_range_control']:
            if value < parameter['min']:
                value = parameter['min']
            if value > parameter['max']:
                value = parameter['max']
                #value = round((value - parameter['min']) / parameter['step']) * parameter['step']
        elif parameter['is_select_control']:
            try: parameter['indexed_values'][machine_name]
            except:
                keys = parameter['indexed_values']
                value = keys[0]
        values[machine_name] = value
    for value in values:
        pass
#    number_of_blank_lines = 0;
#    output = ''
#    while (($line = fgets($r)) !== FALSE):
#        if (strlen(trim($line)) <= 1) $number_of_blank_lines++;
#        else if ($number_of_blank_lines > 2)
#        $output .= $line;
#    if (pclose($r) != 0)
#    header('HTTP/1.0 500 Internal Server Error');
#    else
#    echo $output;

@route('/ajax/dice', method='POST')
def dice_parse():
    #Populate variables from post
    s = do_session(request)
    process_vars(request.forms, s)




@route('/foo')
def foo():
    s = do_session(request)
    var = 'foo'
    tpl = template('./path/to/foo', var=var)
    return tpl

app = SessionMiddleware(default_app(), session_opts)
application = app
