import yaml
import HTMLParser
import re

htmlp = HTMLParser.HTMLParser()
YAML = file('../parameters.yaml', 'r')
CONF_FILE = yaml.load(YAML)
YAML.close()
basic_help = CONF_FILE['basic_help']
intermediate_help = CONF_FILE['intermediate_help']
advanced_help = CONF_FILE['advanced_help']

def format_for_web(text):
    return re.sub(r'/^\(([^)]+)\)/', '<sup>$1</sup>',
        re.sub(r'/_\(([^)]+)\)/', '<sub>$1</sub>',
            htmlp.unescape(text)))

def is_num(n):
    try: float(n)
    except (ValueError, TypeError), e: print e

def options(p, opts, opt):
    try: p[opt]
    except KeyError: pass
    else: opts.append(opt)

def foo():
    pass
#    #The next 100 lines or so are just checking to make sure all the data for each input is set
#    missing_parameter = "Missing \"%s\" attribute on configuration element."
#    too_many_items = "Configuration_element has %d extra element(s)."
#    option_no_name = "Parameter option element has no \"name\" option and should."
#    option_no_machine_name = "Parameter option element has no \"machine_name\" option and should."
#    non_numeric_configuration = "The \"min,\" \"max,\" and \"step\" options are numeric."
#    duplicate_property = "Multiple parameters with machine name \"%s\"."
#    duplicate_option = "Multiple options with machine_name \"%s\"."
#    invalid_default = "The default must be between the minimum and maximum."
#    no_graph_in_location = "There is no graph set to display in location %s."
#    tabs = {}
#    all_parameters = {}
#    selected_tab = None
#    graphs = {}
#    graph_locations = ['topleft', 'topright', 'bottomleft', 'bottomright']

def get_tabs():
    tabs, parameters, all_parameters, selected = build_data()
    return tabs

def get_selected_tab():
    tabs, parameters, all_parameters, selected = build_data()
    return selected

def get_parameters():
    tabs, parameters, all_parameters, selected = build_data()
    return parameters

def get_all_parameters():
    tabs, parameters, all_parameters, selected = build_data()
    return all_parameters

def get_measurements():
    measurements, graphs, graph_locations = build_measurements()
    return measurements

def get_graphs():
    measurements, graphs, graph_locations = build_measurements()
    return graphs

def get_graph_locations():
    measurements, graphs, graph_locations = build_measurements()
    return graph_locations

def build_data():
    parameters = CONF_FILE['parameters']
    tabs = {}
    all_parameters = {}
    selected_tab = 'basic'
    for parameter in parameters:
        is_select_control = False
        is_range_control = False
        is_submit_control = False
        required = ["name", "machine_name", "section", "tab"]
        optional = []
        try: parameter['min']
        except KeyError: parameter['is_range_control'] = False
        else:
            required.extend(["min", "max", "default", "precision"])
            is_range_control = True
            parameter['is_range_control'] = True
        try: parameter['values']
        except KeyError: parameter['is_select_control'] = False
        else:
            required.append('values')
            is_select_control = True
            parameter['is_select_control'] = True
        try: parameter['id']
        except KeyError: parameter['is_submit_control'] = False
        else:
            required.extend(['id', 'button_name'])
            is_submit_control = True
            parameter['is_submit_control'] = True
        options(parameter, optional, 'step')
        options(parameter, optional, 'description')
        options(parameter, optional, 'unit')
        options(parameter, optional, 'subheading')
        options(parameter, optional, 'disabled')
        size = len(required) + len(optional)
        #        if len(parameter) > size:
        #PHP:            trigger_error(sprintf(too_many_items, count(parameter) - size), E_USER_ERROR);
        #        for name in required:
        #PHP:            if (!isset(parameter[name]))
        #PHP:            trigger_error(sprintf(missing_parameter, name), E_USER_ERROR);
        name = parameter['name']
        machine_name = parameter['machine_name']
        tab_name = parameter['tab']
        cleaned_tab_name = re.sub(r'[^a-z]', '', str(parameter['tab']).lower())
        section_name = parameter['section']
        cleaned_section_name = re.sub(r'[^a-z]', '', str(parameter['section']).lower())
        if is_select_control:
            parameter['indexed_values'] = {}
            values = parameter['values']
            for value in values:
                try: value['name']
                except KeyError: pass #trigger_error(option_no_name, E_USER_ERROR);
                try: value['machine_name']
                except KeyError: pass #trigger_error(option_no_machine_name, E_USER_ERROR);
                option_machine_name = value['machine_name']
                try: parameter['indexed_values'][option_machine_name]
                except KeyError: pass #trigger_error(duplicate_option, E_USER_ERROR);
                parameter['indexed_values'][option_machine_name] = value
        elif is_range_control:
            pass
        #            if (!is_numeric(parameter['min']) ||
        #            !is_numeric(parameter['max']) ||
        #            !is_numeric(parameter['step']) ||
        #            !is_numeric(parameter['precision']) ||
        #            !is_numeric(parameter['default']))
        #            trigger_error(non_numeric_configuration, E_USER_ERROR);
        #
        #            if ((parameter['default'] > parameter['max']) ||
        #            (parameter['default'] < parameter['min']))
        #            trigger_error(invalid_default, E_USER_ERROR);
        #            }
        try: all_parameters[machine_name]
        except KeyError, e:
            all_parameters[machine_name] = parameter
        #        else: print e
        try: tabs[cleaned_tab_name]
        except KeyError:
            tabs[cleaned_tab_name] = {
                'name': tab_name,
                'sections': {},
                'html_id': 'tab-'+cleaned_tab_name,
                }
            if selected_tab is None:
            #                selected_tab = &tabs[cleaned_tab_name]
                selected_tab = tabs[cleaned_tab_name]

        try: tabs[cleaned_tab_name]['sections'][cleaned_section_name]
        except:
            tabs[cleaned_tab_name]['sections'][cleaned_section_name] = {
                'name': section_name,
                'parameters': [],
                }
        tabs[cleaned_tab_name]['sections'][cleaned_section_name]['parameters'].append(parameter)
    return tabs, parameters, all_parameters, selected_tab

def build_measurements():
    measurements = CONF_FILE['measurements']
    graphs = {}
    graph_locations = ['topleft', 'topright', 'bottomleft', 'bottomright']
    for measurement in measurements:
        required = ['name', 'machine_name', 'unit']
        optional = []
        for name in required:
            try: measurement[name]
            except KeyError, e: pass
        options(measurement, optional, 'description')
        options(measurement, optional, 'format')
        options(measurement, optional, 'location')
        size = len(required) + len(optional)
        #        if (count($measurement) > $size)
        #        trigger_error(sprintf($too_many_items, count($measurement) - $size), E_USER_ERROR);
        try: measurement['location']
        except KeyError, e: pass
        else:
            location = measurement['location']
            try: graphs[location]
            except KeyError:
                graphs[location] = measurement
            #            else: trigger_error(sprintf($duplicate_graph, $location), E_USER_ERROR);
    for location in graph_locations:
        try: graphs[location]
        except KeyError, e: pass
    return measurements, graphs, graph_locations

def build_questions():
    questions = CONF_FILE['questions']
    for question in questions:
        required = ['question', 'answer']
        for name in required:
            try: question[name]
            except: pass
            else: pass #trigger_error(sprintf(missing_parameter, name), E_USER_ERROR);
        size = len(required)
        if len(question) > size:
            pass #trigger_error(sprintf(too_many_items, count(measurement) - size), E_USER_ERROR);

def tabs_html():
    tabs = get_tabs()
    selected_tab = get_selected_tab()
    html = ''
    if len(tabs) <= 1:
        html += '<div id="parameters">\n'
    else:
        html += '<div id="parameters" class="has-tabs">\n'
    html += '<div id="sidebar-tabs" class="tabs">\n'
    for tab in tabs:
        tab_name = format_for_web(tabs[tab]['name'])
        tab_id = htmlp.unescape(tabs[tab]['html_id'])
        if tab == selected_tab:
            html += '<a href="" class="selected" id="link-to-'+tab_id+'">'+tab_name+'</a>\n'
        else:
            html += '<a href="" id="link-to-'+tab_id+'">'+tab_name+'</a>\n'
    html += '</div>\n'
    for tab in tabs:
        tab_id = htmlp.unescape(tabs[tab]['html_id'])
        sections = tabs[tab]['sections']
        if tab == selected_tab:
            html += '<div id="'+tab_id+'" class="tab selected">\n'
        else:
            html += '<div id="'+tab_id+'" class="tab notselected">\n'
        for section in sections:
            section_name = format_for_web(sections[section]['name'])
            parameters = sections[section]['parameters']
            html += '<h2>'+section_name+'</h2>\n'
            html += '<ul>\n'
            for parameter in parameters:
            #                    name = format_for_web(parameter['name'])
                name = parameter['name']
                machine_name = htmlp.unescape(parameter['machine_name'])
                is_select_control = parameter['is_select_control']
                is_range_control = parameter['is_range_control']
                is_submit_control = parameter['is_submit_control']
                try: parameter['disabled']
                except:
                    disabled = ''
                    clas = ''
                else:
                    disabled = 'disabled="disabled"'
                    clas = 'class="disabled"'
                try: parameter['description']
                except:
                    try: parameter['unit']
                    except: html += '<li><label %s>%s ' % (clas, name)
                    else:
                        unit = parameter['unit']
                        html += '<li %s>%s (%s) ' % (clas, name, unit)
                else:
                    try: parameter['unit']
                    except:
                        description = htmlp.unescape(parameter['description'])
                        html += '<li><label title="%s" %s>%s ' % (description, clas, name)
                    else:
                        unit = parameter['unit']
                        description = htmlp.unescape(parameter['description'])
                        html += '<li><label title="%s" %s>%s (%s) ' % (description, clas, name, unit)
                if is_select_control:
                    html += '</label>\n'
                    values = parameter['values']
                    html += '<select name="%s" %s>\n' % (machine_name, disabled)
                    for value in values:
                        option_machine_name = value['machine_name']
                        option_name = value['name'];
                        try: value['description']
                        except: html += '<option name="%s">%s</option>\n' % (option_machine_name, option_name)
                        else:
                            description = htmlp.unescape(value['description'])
                            html += '<option name="%s" ' % option_machine_name
                            html += 'title="%s">%s</option>\n' % (description, option_name)
                    html += '</select></li>\n'
                elif is_range_control:
                    min = parameter['min']
                    max = parameter['max']
                    step = parameter['step']
                    default = parameter['default']
                    precision = parameter['precision']
                    tickMarkLeft = float((default - min)/(max - min)) * 100.
                    tickMarkLeft = tickMarkLeft - 50
                    tickMarkLeftWithUnit = '%i%%' % tickMarkLeft
                    html += '<span class="label">%s</span></label> <input name="%s" %s ' % (
                        default, machine_name, disabled)
                    html += 'type="range" min="%s" max="%s" step="%s" value="%s" data-prec="%s"/>\n' % (
                        min, max, step, default, precision)
                    html += '<div class="tick-wrap"><span class="tick" style="left:%s" %s>&bullet;</span></div></li>\n' % (
                        tickMarkLeftWithUnit, clas)
                elif is_submit_control:
                    id = parameter['id']
                    button_name = parameter['button_name']
                    html += '</label><input type="submit" id="%s" value="%s"/></li>' % (id, button_name)
            html += '</ul>\n'
        html += '</div>'
    return html

def paragraphs_html():
    initial_help = CONF_FILE['initial_help']
    html = ''
    paragraphs = initial_help.split('\n')
    for paragraph in paragraphs:
        html += '<p>%s</p>\n' % paragraph
    return html

def measurements_html():
    measurements = get_measurements()
    html = ''
    for measurement in measurements:
        machine_name = htmlp.unescape(measurement['machine_name'])
        measurement_name = htmlp.unescape(measurement['name'])
        html += '<option value="%s">%s</option>\n' % (machine_name, measurement_name)
    return html

