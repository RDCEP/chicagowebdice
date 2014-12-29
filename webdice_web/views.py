from __future__ import division
import json
import zipfile
import csv
import StringIO
import os
from numpy import inf
from lxml import etree
from flask import render_template, request, Blueprint, jsonify, send_file
from webdice.dice import Dice2010, Dice2013
from webdice_web.constants import BASE_DIR


mod = Blueprint('webdice', __name__, static_folder='static',
                template_folder='templates')


def validate_number(n):
    """Currently unused. This is a stub for number validation
    before passing values to the Dice2007 object."""
    try: float(n)
    except ValueError: raise Exception('Input needs to be a number.')
    else: return n


def run_loop(form, year=2013):

    dice = Dice2010() if year == 2010 else Dice2013()

    for field in ['e2050', 'e2100', 'e2150']:
        form[field] = float(form[field]) / 100

    for field in ['p2050', 'p2100', 'p2150']:
        form[field] = float(form[field]) / 100

    for p in dice.user_params:
        try:
            setattr(dice.params, p, float(form[p]))
        except KeyError:
            pass
        except ValueError:
            pass

    dice.params.productivity_model = 'dice_backstop_2013' if year == 2010 else 'dice_2013'

    try:
        dice.params.carbon_model = form['carbon_model']
        dice.params.damages_model = form['damages_model']
    except KeyError:
        dice.params.carbon_model = 'dice_{}'.format(year)
        dice.params.damages_model = 'dice_{}'.format(year)

    opt = False
    dice.params.treaty = False
    dice.params.carbon_tax = False
    policy = form['policy_type']
    if policy == 'treaty':
        dice.params.treaty = True
    elif policy == 'optimized':
        opt = True
    elif policy == 'carbon_tax':
        dice.params.carbon_tax = True
    dice.loop(opt=opt)
    out = dice.format_output()
    out['data'] = {
        k: [l if l > -inf else -999 for l in v] for k, v in out['data'].iteritems()
    }
    return jsonify(**out)


@mod.route('/')
def index():
    """Returns index page."""
    return render_template(
        'index.html',
    )


@mod.route('/documentation')
def documentation():
    """Returns index page."""
    return render_template(
        'modules/documentation/index.html',
    )


@mod.route('/glossary')
def glossary():
    """Returns index page."""
    return render_template(
        'modules/glossary/index.html',
    )


@mod.route('/glossary/<term>')
def glossary_term(term):
    """Returns index page."""
    return render_template(
        'modules/glossary/static_page.html',
        term=term
    )


@mod.route('/glossary/advanced/<term>')
def glossary_advanced_term(term):
    """Returns index page."""
    s = ''
    f = os.path.join(BASE_DIR, 'templates', 'modules', 'glossary', 'terms',
                     'advanced', '{}.html'.format(term))
    with open(f) as f:
        s = f.read()
    return s


@mod.route('/advanced')
def advanced():
    return render_template(
        'versions/advanced.html',
        dice_version=2013,
        time_step=5,
        start_year=2010,
    )


@mod.route('/standard')
def standard():
    return render_template(
        'versions/standard.html',
        dice_version=2013,
        time_step=5,
        start_year=2010,
    )


@mod.route('/run/standard', methods=['POST', 'GET'])
def graphs_standard():
    form = json.loads(request.data)
    new_data = {
        'temp_co2_doubling': [1, 2, 3.2, 4, 5],
        'damages_exponent': [1, 1.4, 2.0, 2.8, 4.0],
        'productivity_decline': [.015, .011, .009, .003, 0.0],
        'backstop_decline': [0.20, 0.10, 0.05, 0.025, 0.0],
        'intensity_decline_rate': [.060, .02, .006, .0006, 0.0],
    }
    for field in new_data.keys():
        try:
            if form[field]:
                form[field] = new_data[field][int(form[field]) - 1]
        except KeyError:
            pass

    for field in ['depreciation', 'savings', 'prstp', 'prod_frac', ]:
        try:
            if form[field]:
                form[field] = float(form[field]) / 100
        except KeyError:
            pass

    return run_loop(form, year=2013)


@mod.route('/run/advanced', methods=['POST', 'GET'])
def graphs_advanced():
    """
    Get data from <form>, run DICE loop.
    ...
    Args:
        None
    Returns:
        Formatted step values
    """
    form = json.loads(request.data)
    for field in ['depreciation', 'savings', 'prstp', 'backstop_decline',
                  'productivity_decline', 'intensity_decline_rate',
                  'prod_frac', ]:
        try:
            if form[field]:
                form[field] = float(form[field]) / 100
        except KeyError:
            pass

    return run_loop(form, year=2013)


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