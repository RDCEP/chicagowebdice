import json
import zipfile
import StringIO
from datetime import datetime

from flask import render_template, request, make_response, Blueprint, jsonify
from flask import send_file

from webdice.dice import Dice2007, Dice2010
from webdice_web.html_parser.web import DiceWebParser


mod = Blueprint('webdice', __name__, static_folder='static',
                template_folder='templates')


def validate_number(n):
    """Currently unused. This is a stub for number validation
    before passing values to the Dice2007 object."""
    try: float(n)
    except ValueError: raise Exception('Input needs to be a number.')
    else: return n


def do_session(request, year=None):
    """
    Checks for existence of session data. Writes variables as necessary.
    ...
    Keyword Arguments:
    newdice: obj
        A Dice2007 object.
    """
    dice = False
    s = request.environ.get('beaker.session')
    if 'dice' not in s:
        if year == 2010:
            dice = Dice2010()
        else:
            dice = Dice2007()
        s['dice'] = dice
    if year is not None and s['dice'].params.dice_version != year:
        if year == 2007:
            dice = Dice2007()
        elif year == 2010:
            dice = Dice2010()
    s['dice'] = dice if dice else s['dice']
    return s, DiceWebParser(year)


@mod.route('/')
def index():
    """Returns index page."""
    s, parser = do_session(request, 2007)
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    return render_template(
        'index.html',
        now=now,
        paragraphs_html=parser.paragraphs_html('index'),
    )


@mod.route('/advanced/<int:year>')
def advanced(year):
    s, parser = do_session(request, year)
    tabs = parser.get_advanced_tabs()
    return page(tabs, parser, year, 'advanced_{}'.format(year))


@mod.route('/standard')
def standard():
    s, parser = do_session(request, 2007)
    tabs = parser.get_basic_tabs()
    return page(tabs, parser, None, 'standard')


def page(tabs, parser, year, tpl='index'):
    """
    Return HTML for all pages.
    ...
    Args:
        None
    Returns:
        HTML
    """
    measurements = parser.get_measurements()
    # tabs = get_tabs()
    all_parameters = parser.get_all_parameters()
    without_sections = []
    for s in measurements:
        for m in s['options']:
            without_sections.append(m)
    graph_locations = ['topleft', 'topright', 'bottomleft', 'bottomright', ]
    graph_names = ['essential', 'climate', 'economy', 'policy']
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
        paragraphs_html=parser.paragraphs_html(tpl.split('_')[0]),
        all_parameters=all_parameters,
        now=now,
        dice_version=year,
        other_versions=[x for x in [2007, 2010] if x != year],
    )


@mod.route('/run/standard', methods=['POST', 'GET'])
def graphs_standard():
    s, parser = do_session(request, 2010)
    this_dice = s['dice']
    this_dice.loop()
    form = json.loads(request.data)
    new_data = {
        'temp_co2_doubling': [1, 2, 3.2, 4, 5],
        'damages_exponent': [1, 1.4, 2.0, 2.8, 4.0],
        'productivity_decline': [.015, .011, .009, .003, 0.0],
        'backstop_ratio': [1, 1.4, 2.0, 2.8, 4.0],
        'intensity_decline_rate': [.060, .02, .0065, .0006, 0.0],
    }
    for field in new_data.keys():
        try:
            if form[field]:
                form[field] = new_data[field][int(form[field]) - 1]
        except KeyError:
            pass

    all_parameters = parser.get_all_parameters()

    for p in all_parameters:
        try:
            p['disabled']
        except (KeyError, AttributeError):
            try:
                getattr(this_dice.params, p['machine_name'])
            except AttributeError:
                pass
            else:
                try:
                    this_dice.params.__dict__[p['machine_name']] = float(form[p['machine_name']])
                except (ValueError, AttributeError, KeyError):
                    pass
    this_dice.params.carbon_model = 'dice_2007'
    this_dice.params.damages_model = 'dice_2007'
    opt = False
    policy = form['policy_type']
    this_dice.params._treaty = False
    this_dice.params._carbon_tax = False
    if policy == 'treaty':
        this_dice.params._treaty = True
    elif policy == 'optimized':
        opt = True
    elif policy == 'carbon_tax':
        this_dice.params._carbon_tax = True
    this_dice.loop(opt=opt)
    return jsonify(**this_dice.format_output())


@mod.route('/run/<int:year>', methods=['POST', 'GET'])
def graphs_d3(year=2007):
    """
    Get data from <form>, run DICE loop.
    ...
    Args:
        None
    Returns:
        Formatted step values
    """
    s, parser = do_session(request, year)
    this_dice = s['dice']
    this_dice.loop()
    form = json.loads(request.data)
    for field in ['depreciation', 'savings', 'prstp', 'backstop_decline',
                  'productivity_decline', 'intensity_decline_rate',
                  'prod_frac', ]:
        try:
            if form[field]:
                form[field] = float(form[field]) / 100
        except KeyError:
            pass

    all_parameters = parser.get_all_parameters()

    for p in all_parameters:
        try:
            p['disabled']
        except (KeyError, AttributeError):
            try:
                getattr(this_dice.params, p['machine_name'])
            except AttributeError:
                pass
            else:
                try:
                    this_dice.params.__dict__[p['machine_name']] = float(form[p['machine_name']])
                except (ValueError, AttributeError, KeyError):
                    pass
    try:
        this_dice.params.damages_model = form['damages_model']
        this_dice.params.carbon_model = form['carbon_model']
        # this_dice.params.temperature_model = form['temperature_model']
    except KeyError:
        this_dice.params.carbon_model = 'dice_2007'
        this_dice.params.damages_model = 'dice_2007'
    opt = False
    policy = form['policy_type']
    this_dice.params._treaty = False
    this_dice.params._carbon_tax = False
    if policy == 'treaty':
        this_dice.params._treaty = True
    elif policy == 'optimized':
        opt = True
    elif policy == 'carbon_tax':
        this_dice.params._carbon_tax = True
    this_dice.loop(opt=opt)
    return jsonify(**this_dice.format_output())


@mod.route('/zip_svgs', methods=['POST', ])
def zip_svgs():
    # form = json.loads(request.data)
    form = request.form
    buffer = StringIO.StringIO()
    zipped = zipfile.ZipFile(buffer, 'w')
    for k in form.keys():
        s = StringIO.StringIO()
        s.write(str(form[k]))
        zipped.writestr('{}.svg'.format(k), s.getvalue())
    zipped.close()
    buffer.seek(0)
    return send_file(buffer, attachment_filename='{}.zip'.format('WebDICE-SVGs'),
                     as_attachment=True)
    # response = make_response(buffer)
    # response.headers['Content-Disposition'] = 'attachment; filename="{}.zip"'.format('WebDICE-SVGs')
    # return response


@mod.route('/csv', methods=['POST',])
def csv_output():
    data = request.form['data']
    response = make_response(data)
    response.headers['Content-Disposition'] = 'attachment; filename="{}.csv"'.\
        format('WebDICE-Data')
    return response
