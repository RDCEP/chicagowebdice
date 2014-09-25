from __future__ import division
import json
import zipfile
import csv
import StringIO
from numpy import inf
from lxml import etree
from datetime import datetime
from flask import render_template, request, Blueprint, jsonify
from flask import send_file
from webdice.dice import Dice2007, Dice2010


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
    return s


def run_loop(this_dice, form, year=2010):

    for field in ['e2050', 'e2100', 'e2150']:
        form[field] = float(form[field]) / 100

    for field in ['p2050', 'p2100', 'p2150']:
        form[field] = float(form[field]) / 100

    for p in this_dice.user_params:
        try:
            setattr(this_dice.params, p, float(form[p]))
        except KeyError:
            pass
        except ValueError:
            pass

    try:
        this_dice.params.damages_model = form['damages_model']
        this_dice.params.carbon_model = form['carbon_model']
    except KeyError:
        this_dice.params.carbon_model = 'dice_{}'.format(year)
        this_dice.params.damages_model = 'dice_{}'.format(year)

    opt = False
    policy = form['policy_type']
    this_dice.params.treaty = False
    this_dice.params.carbon_tax = False
    if policy == 'treaty':
        this_dice.params.treaty = True
    elif policy == 'optimized':
        opt = True
    elif policy == 'carbon_tax':
        this_dice.params.carbon_tax = True
    this_dice.loop(opt=opt)
    out = this_dice.format_output()
    out['data'] = {
        k: [l if l > -inf else -999 for l in v] for k, v in out['data'].iteritems()
    }
    return jsonify(**out)


@mod.route('/')
def index():
    """Returns index page."""
    s = do_session(request, 2007)
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    return render_template(
        'index.html',
        now=now,
    )


@mod.route('/advanced')
def advanced():
    return render_template(
        'versions/advanced_2010.html',
        now = datetime.now().strftime('%Y%m%d%H%M%S'),
        dice_version=2010,
    )


@mod.route('/standard')
def standard():
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    return render_template(
        'versions/standard.html',
        now=now,
    )


@mod.route('/run/standard', methods=['POST', 'GET'])
def graphs_standard():
    s = do_session(request, 2010)
    this_dice = s['dice']
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

    for field in ['depreciation', 'savings', 'prstp', 'backstop_decline',
                  'prod_frac', ]:
        try:
            if form[field]:
                form[field] = float(form[field]) / 100
        except KeyError:
            pass

    return run_loop(this_dice, form)


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
    s = do_session(request, year)
    this_dice = s['dice']
    form = json.loads(request.data)
    for field in ['depreciation', 'savings', 'prstp', 'backstop_decline',
                  'productivity_decline', 'intensity_decline_rate',
                  'prod_frac', ]:
        try:
            if form[field]:
                form[field] = float(form[field]) / 100
        except KeyError:
            pass

    return run_loop(this_dice, form, year)


@mod.route('/get_svg', methods=['POST', ])
def get_svg():
    def combine_custom(c, t):
        ns = 'http://www.w3.org/2000/svg'
        c = etree.fromstring(c)
        t = etree.fromstring(t)
        cg = c.xpath('/n:svg/n:g', namespaces={'n': ns})
        tg = t.xpath('/n:svg/n:g', namespaces={'n': ns})
        tgg = tg[1].xpath('./n:g', namespaces={'n': ns})
        c.append(tg[0])
        for t in tgg:
            cg[1].append(t)
        return etree.tostring(c)
    form = request.form
    buffer = StringIO.StringIO()
    zipped = zipfile.ZipFile(buffer, 'w')
    for k in form.keys():
        s = StringIO.StringIO()
        if k == 'custom_graph':
            s.write(combine_custom(str(form['custom_graph']),
                                   str(form['twin_graph'])))
        else:
            s.write(str(form[k]))
        zipped.writestr('{}.svg'.format(k), s.getvalue())
    zipped.close()
    buffer.seek(0)
    return send_file(buffer,
                     attachment_filename='{}.zip'.format('WebDICE-SVGs'),
                     as_attachment=True)


@mod.route('/get_csv', methods=['POST',])
def get_csv():
    buffer = StringIO.StringIO()
    data = json.loads(request.form['data'])
    writer = csv.writer(buffer)
    for run in data.keys():
        writer.writerow([data[run]['name']])
        writer.writerow(data[run]['parameters'].keys())
        writer.writerow(data[run]['parameters'].values())
        for var in data[run]['data'].keys():
            writer.writerow([var] + data[run]['data'][var])
    buffer.seek(0)
    return send_file(buffer,
                     attachment_filename='{}.csv'.format('WebDICE-CSV'),
                     as_attachment=True)