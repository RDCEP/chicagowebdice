import yaml
import HTMLParser
import re
import pprint


pp = pprint.PrettyPrinter(indent=4)
htmlp = HTMLParser.HTMLParser()
YAML = file('../parameters2.yaml', 'r')
CONF_FILE = yaml.load(YAML)
YAML.close()

def format_for_web(text):
    return re.sub(
        r'/^\(([^)]+)\)/', '<sup>$1</sup>',
        re.sub(
            r'/_\(([^)]+)\)/', '<sub>$1</sub>',
            htmlp.unescape(text)
        )
    )

def get_defaults(section):
    defaults = {}
    for var in ['min', 'max', 'step', 'default', 'precision']:
        try:
            defaults[var] = section[var]
        except:
            defaults[var] = False
    return defaults

def set_from_defaults(parameter, defaults):
    for key, val in defaults.iteritems():
        if val is not False:
            try:
                parameter[key]
            except KeyError:
                parameter[key] = val
    print parameter
    return parameter

def set_input_type(parameter, key, type):
    try:
        parameter[key]
    except KeyError:
        parameter[type] = False
    else:
        parameter[type] = True

def set_tick(parameter):
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

def get_parameters(section):
    try:
        parameters = section['parameters']
    except KeyError:
        parameters = []
    return parameters

def get_sections(tab):
    try:
        sections = tab['sections']
    except:
        sections = []
    return sections

def get_radio(section):
    try:
        radio = section['radio']
        return True
    except:
        return False

def get_tabs():
    tabs = CONF_FILE['tabs']
    for tab in [tabs[0]]:
        print tab
        policy = False
        if tab['name'] == 'Policy':
            policy = True
        for section in get_sections(tab):
            print section['name']
            defaults = get_defaults(section)
            if policy and get_radio(section):
                button = '<input type="radio" value="treaty" name="policy_type" style="width:auto"'
                if section['machine_name'] == 'default':
                    button += ' checked="checked"'
                button += '/>'
                section['name'] = button + section['name']
            parameters = get_parameters(section)
            for parameter in parameters:
                parameter = set_from_defaults(parameter, defaults)
                parameter = set_input_type(parameter, 'min', 'range')
                parameter = set_input_type(parameter, 'values', 'select')
                parameter = set_tick(parameter)



                # pp.pprint( tabs[0])
                # for subsection in get_sections(section):

                # for numinput in section['parameters']:
                #     numinput['disabled'] = True
                #     print numinput
