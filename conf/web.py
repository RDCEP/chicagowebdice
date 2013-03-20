import yaml
import HTMLParser
import re


htmlp = HTMLParser.HTMLParser()
YAML = file('parameters.yaml', 'r')
CONF_FILE = yaml.load(YAML)
YAML.close()

def format_for_web(text):
    """
    Replace ^(N) with superscript and _(N) with subscript
    """
    return re.sub(
        r'/^\(([^)]+)\)/', '<sup>$1</sup>',
        re.sub(
            r'/_\(([^)]+)\)/', '<sub>$1</sub>',
            htmlp.unescape(text)
        )
    )

def get_defaults(section):
    """
    Return default input attribute values for range inputs in section
    """
    defaults = {}
    for var in [
        'min', 'max', 'step', 'default', 'precision', 'unit', 'init_disabled'
    ]:
        try:
            defaults[var] = section[var]
        except:
            defaults[var] = False
    return defaults

def set_from_defaults(parameter, defaults):
    """
    Set values of parameter based on section defaults
    """
    for key, val in defaults.iteritems():
        if val is not False:
            try:
                parameter[key]
            except KeyError:
                parameter[key] = val
    return parameter

def set_input_type(parameter, key, input_type):
    """
    Discern input type from parameter key
    """
    try:
        parameter[key]
    except KeyError:
        pass
    else:
        parameter['type'] = input_type
    return parameter

def set_tick(parameter):
    """
    Calculate position of slider tick mark
    """
    try:
        parameter['unit']
    except KeyError:
        parameter['unit'] = ''
    minimum = parameter['min']
    maximum = parameter['max']
    default = parameter['default']
    parameter['tick'] = '%i%%' % (
        (((float(default) - minimum)/(maximum - minimum)) * 100.) - 50.
    )
    return parameter

def get_parameters(section):
    """
    Select parameters based on section
    """
    try:
        parameters = section['parameters']
    except KeyError:
        parameters = []
    return parameters

def get_sections(tab):
    """
    Select sections based on tab
    """
    try:
        sections = tab['sections']
    except:
        sections = []
    return sections

def is_radio(section):
    """
    Determine if section should be preceded by a radio button
    """
    try:
        section['radio']
    except KeyError:
        return False
    return True

def get_advanced_tabs():
    tabs, parameters = parse_conf()
    return tabs

def get_all_parameters():
    tabs, parameters = parse_conf()
    return parameters

def parse_conf():
    tabs = CONF_FILE['tabs']
    all_parameters = []
    for tab in tabs:
        policy = False
        if tab['name'] == 'Policy':
            policy = True
        for section in get_sections(tab):
            defaults = get_defaults(section)
            if policy and is_radio(section):
                button = '<input type="radio" value="'
                button += section['machine_name']
                button += '" name="policy_type" style="width:auto"'
                if section['machine_name'] == 'default':
                    button += ' checked="checked"'
                button += '/>'
                section['radio'] = button
            parameters = get_parameters(section)
            for parameter in parameters:
                parameter = set_from_defaults(parameter, defaults)
                parameter = set_input_type(parameter, 'min', 'range')
                parameter = set_input_type(parameter, 'options', 'select')
                if parameter['type'] == 'range':
                    parameter = set_tick(parameter)
                parameter = get_parameter_help(parameter)
                all_parameters.append(parameter)
    return [tabs, all_parameters]

def get_basic_tabs():
    tabs = CONF_FILE['basic_tabs']
    for tab in tabs:
        policy = False
        if tab['name'] == 'Policy':
            policy = True
        for section in get_sections(tab):
            defaults = get_defaults(section)
            if policy and is_radio(section):
                button = '<input type="radio" value="'
                button += section['machine_name']
                button += '" name="policy_type" style="width:auto"'
                if section['machine_name'] == 'default':
                    button += ' checked="checked"'
                button += '/>'
                section['radio'] = button
            parameters = get_parameters(section)
            for parameter in parameters:
                parameter = set_from_defaults(parameter, defaults)
                parameter = set_input_type(parameter, 'min', 'range')
                parameter = set_input_type(parameter, 'options', 'select')
                if parameter['type'] == 'range':
                    parameter = set_tick(parameter)
                parameter = get_parameter_help(parameter)
    return tabs


def set_options(p, opts, opt):
    try:
        p[opt]
    except KeyError:
        pass
    else:
        opts.append(opt)

def get_measurements():
    measurements = CONF_FILE['measurements']
    return measurements

def paragraphs_html(t):
    """
    Build HTML for initial text on webpage.
    ...
    Args: None
    Returns:
        HTML
    """
    initial_help = CONF_FILE['initial_help'][t]
    html = ''
    paragraphs = initial_help.split('\n')
    for paragraph in paragraphs:
        html += '<p>%s</p>\n' % paragraph
    return html

def get_parameter_help(parameter):
    parameters_help = CONF_FILE['parameter_help']
    try:
        parameter_help = parameters_help[parameter['machine_name']]
        html = ''
        paragraphs = parameter_help.split('\n')
        for paragraph in paragraphs:
            html += '<p>%s</p>\n' % paragraph
        parameter['help'] = html
    except:
        pass
    return parameter