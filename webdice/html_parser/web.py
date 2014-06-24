import yaml
import HTMLParser
import re
import os
from webdice.constants import BASE_DIR


class DiceWebParser(object):
    def __init__(self, year=2010):
        self.htmlp = HTMLParser.HTMLParser()
        YAML = file(os.path.join(BASE_DIR, 'html_parser',
                                 'parameters_2010.yaml'), 'r')
        if year == 2007:
            YAML = file(os.path.join(BASE_DIR, 'html_parser',
                                     'parameters.yaml'), 'r')
        self.CONF_FILE = yaml.load(YAML)
        YAML.close()

    def format_for_web(self, text):
        """
        Replace ^(N) with superscript and _(N) with subscript
        """
        return re.sub(
            r'/^\(([^)]+)\)/', '<sup>$1</sup>',
            re.sub(
                r'/_\(([^)]+)\)/', '<sub>$1</sub>',
                self.htmlp.unescape(text)
            )
        )

    def get_defaults(self, section):
        """
        Return default input attribute values for range inputs in section
        """
        defaults = {}
        for var in [
            'min', 'max', 'step', 'default', 'precision', 'unit', 'init_disabled', 'class'
        ]:
            try:
                defaults[var] = section[var]
            except:
                defaults[var] = False
        return defaults

    def set_from_defaults(self, parameter, defaults):
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

    def set_input_type(self, parameter, key, input_type):
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

    def set_tick(self, parameter):
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

    def get_parameters(self, section):
        """
        Select parameters based on section
        """
        try:
            parameters = section['parameters']
        except KeyError:
            parameters = []
        return parameters

    def get_sections(self, tab):
        """
        Select sections based on tab
        """
        try:
            sections = tab['sections']
        except:
            sections = []
        return sections

    def is_radio(self, section):
        """
        Determine if section should be preceded by a radio button
        """
        try:
            section['radio']
        except KeyError:
            return False
        return True

    def get_advanced_tabs(self):
        tabs, parameters = self.advanced_tabs()
        return tabs

    def get_all_parameters(self):
        tabs, parameters = self.advanced_tabs()
        return parameters

    def advanced_tabs(self):
        tabs = self.CONF_FILE['advanced_tabs']
        all_parameters = []
        for tab in tabs:
            policy = False
            if tab['name'] == 'Policy':
                policy = True
            for section in self.get_sections(tab):
                defaults = self.get_defaults(section)
                if policy and self.is_radio(section):
                    button = '<input type="radio" value="'
                    button += section['machine_name']
                    button += '" name="policy_type" style="width:auto"'
                    if section['machine_name'] == 'default':
                        button += ' checked="checked"'
                    button += '/>'
                    section['radio'] = button
                    HELP = self.get_parameter_help(section, 'advanced',
                            return_html=True)
                    if HELP is not None:
                        section['help'] = HELP
                        all_parameters.append(section)
                parameters = self.get_parameters(section)
                for parameter in parameters:
                    parameter = self.set_from_defaults(parameter, defaults)
                    parameter = self.set_input_type(parameter, 'min', 'range')
                    parameter = self.set_input_type(parameter, 'options', 'select')
                    if parameter['type'] == 'range':
                        parameter = self.set_tick(parameter)
                    parameter = self.get_parameter_help(parameter, 'advanced')
                    all_parameters.append(parameter)
        return [tabs, all_parameters]

    def get_basic_tabs(self):
        tabs = self.CONF_FILE['basic_tabs']
        for tab in tabs:
            policy = False
            if tab['name'] == 'Policy':
                policy = True
            for section in self.get_sections(tab):
                defaults = self.get_defaults(section)
                if policy and self.is_radio(section):
                    button = '<input type="radio" value="'
                    button += section['machine_name']
                    button += '" name="policy_type" style="width:auto"'
                    if section['machine_name'] == 'default':
                        button += ' checked="checked"'
                    button += '/>'
                    section['radio'] = button
                    section['help'] = self.get_parameter_help(section, 'basic', return_html=True)
                parameters = self.get_parameters(section)
                for parameter in parameters:
                    parameter = self.set_from_defaults(parameter, defaults)
                    parameter = self.set_input_type(parameter, 'min', 'range')
                    parameter = self.set_input_type(parameter, 'options', 'select')
                    if parameter['type'] == 'range':
                        parameter = self.set_tick(parameter)
                    parameter = self.get_parameter_help(parameter, 'basic')
        return tabs

    def set_options(self, p, opts, opt):
        try:
            p[opt]
        except KeyError:
            pass
        else:
            opts.append(opt)

    def get_measurements(self):
        measurements = self.CONF_FILE['measurements']
        return measurements

    def paragraphs_html(self, t):
        """
        Build HTML for initial text on webpage.
        ...
        Args: None
        Returns:
            HTML
        """
        # initial_help = self.CONF_FILE['initial_help'][t]
        html = ''
        paragraphs = self.CONF_FILE['initial_help'][t].split('\n')
        for paragraph in paragraphs:
            html += '<p>%s</p>\n' % paragraph
        return html

    def get_parameter_help(self, parameter, help_type, return_html=False):
        parameters_help = self.CONF_FILE['parameter_help']
        html = None
        try:
            parameter_help = parameters_help[help_type][parameter['machine_name']]
            html = ''
            paragraphs = parameter_help.split('\n')
            for paragraph in paragraphs:
                html += '<p>%s</p>\n' % paragraph
        except:
            pass
        if not return_html:
            parameter['help'] = html
            return parameter
        else:
            return html
