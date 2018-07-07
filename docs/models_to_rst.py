#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2015-2018: Alignak team, see AUTHORS.txt file for contributors
#
# This file is part of Alignak.
#
# Alignak is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Alignak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Alignak.  If not, see <http://www.gnu.org/licenses/>.


from os import walk, path
import imp
from graphviz import Digraph


def generate_relation_graph(resource, resources, resource_filename):
    """
    Generate graphviz of the resource (resource + links to other objects)

    :return:
    """
    dot = Digraph(format='png')
    dot.graph_attr.update(size="7.29,200")
    dot.node(resource)
    for key, value in resources.iteritems():
        style = 'dashed'
        if value == 'True':
            style = 'solid'
        if not key.startswith("_"):
            dot.edge(resource, key, label='', style=style)
    dot.render('_static/' + resource_filename, view=False, cleanup=True)


mypath = '../alignak_backend/models/'
f = []
for (dirpath, dirnames, filenames) in walk(mypath):
    for filename in filenames:
        if filename != '__init__.py':
            f.append(''.join([dirpath, filename]))

for filepath in f:
    expected_class = 'MyClass'
    mod_name, file_ext = path.splitext(path.split(filepath)[-1])
    if file_ext.lower() == '.py':
        py_mod = imp.load_source(mod_name, filepath)

        resource_name = py_mod.get_name()
        if resource_name in ['grafana', 'graphite', 'influxdb', 'statsd', 'timeseriesretention']:
            resource_name = ''.join(['ts_', resource_name])
        elif resource_name in ['alignakdaemon', 'livesynthesis', 'livesynthesisretention']:
            resource_name = ''.join(['ls_', resource_name])
        elif resource_name in ['logcheckresult', 'history']:
            resource_name = ''.join(['log_', resource_name])
        elif resource_name in ['userrestrictrole']:
            pass
        elif resource_name in ['alignakretention']:
            pass
        elif not resource_name.startswith('action'):
            resource_name = ''.join(['config_', resource_name])

        print("Creating: %s" % resource_name)
        target = open(''.join(['resources/', resource_name, '.rst']), 'w')
        target.write('.. _resource-%s:' % (py_mod.get_name()))
        target.write("\n\n")
        title = '%s' % (py_mod.get_name())
        try:
            title = '%s (%s)' % (py_mod.get_name(True), py_mod.get_name())
        except:
            pass
        target.write(title)
        target.write("\n")
        target.write("=" * len(title))
        target.write("\n\n")

        try:
            doc = py_mod.get_doc()
            target.write(doc)
            target.write("\n\n")
        except:
            pass

        target.write(".. image:: ../_static/%s.png\n" % (resource_name))
        target.write("\n\n")
        target.write(".. csv-table:: Properties")
        target.write("\n")
        target.write('   :header: "Property", "Type", "Required", "Default", "Relation"')
        target.write("\n\n")

        schema = py_mod.get_schema()
        relations = {}
        specials = {}
        schema = schema['schema']
        for field in sorted(schema.iterkeys()):
            ltype = schema[field]['type']
            title = schema[field].get('title', '')
            comment = schema[field].get('comment', '')
            allowed = schema[field].get('allowed', None)
            if allowed:
                comment = "%s \n\n Allowed values: %s" % (str(comment), str(allowed))
                print("Allowed: %s" % str(allowed))
            required = ''
            if 'required' in schema[field]:
                if schema[field]['required']:
                    required = 'True'
            default = ''
            if 'default' in schema[field]:
                default = schema[field]['default']
            data_relation = ''
            if schema[field]['type'] == 'objectid':
                data_relation = ":ref:`%s <resource-%s>`" \
                                % (schema[field]['data_relation']['resource'],
                                   schema[field]['data_relation']['resource'])
                if not (schema[field]['data_relation']['resource'] in relations and required == ''):
                    relations[schema[field]['data_relation']['resource']] = required
            if schema[field]['type'] == 'list':
                if 'schema' in schema[field] and 'data_relation' in schema[field]['schema']:
                    data_relation = ":ref:`%s <resource-%s>`" \
                                    % (schema[field]['schema']['data_relation']['resource'],
                                       schema[field]['schema']['data_relation']['resource'])
                    if not (schema[field]['schema']['data_relation']['resource'] in relations and
                            required == ''):
                        relations[schema[field]['schema']['data_relation']['resource']] = required
                    ltype = "objectid list"

            csv_line = '   "| %s%s", "**%s**", "**%s**", "**%s**", "%s"\n'
            if required == '':
                csv_line = csv_line.replace('**', '')
            target.write(csv_line
                         % (":ref:`%s <%s-%s>`"
                            % (field, py_mod.get_name(), field) if comment else field,
                            '\n   | *%s*' % title if title else '',
                            ltype, required, default, data_relation))

        for field in sorted(schema.iterkeys()):
            comment = schema[field].get('comment', '')
            allowed = schema[field].get('allowed', None)
            if allowed:
                comment = "%s\n\n   Allowed values: %s" % (str(comment), str(allowed))
            if not comment:
                continue

            required = schema[field].get('required', False)

            target.write('.. _%s-%s:\n\n' % (py_mod.get_name(), field))
            csv_line = '``%s``: %s\n\n'
            if not required:
                csv_line = csv_line.replace('**', '')
            target.write(csv_line % (field, comment))

        target.write("\n\n")
        target.close()

        generate_relation_graph(py_mod.get_name(), relations, resource_name)
