#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2015-2015: Alignak team, see AUTHORS.txt file for contributors
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
    dot.render('resources/_static/' + resource_filename, view=False, cleanup=True)


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
        if not resource_name.startswith('live'):
            if not resource_name.startswith('retention'):
                if not resource_name.startswith('log'):
                    if not resource_name.startswith('action'):
                        resource_name = ''.join(['config', resource_name])

        target = open(''.join(['resources/', resource_name, '.rst']), 'w')
        target.write('.. _resource-%s:' % (py_mod.get_name()))
        target.write("\n\n")
        target.write(py_mod.get_name())
        target.write("\n\n")
        target.write(".. image:: _static/%s.png\n" % (resource_name))
        target.write("\n")
        target.write("===================\n\n")
        target.write(".. csv-table::")
        target.write("\n")
        target.write("   :header: \"Parameter\", \"Type\", \"Required\", \"Default\", \"Data relation\"")
        target.write("\n\n")

        schema = py_mod.get_schema()
        relations = {}
        for line in schema['schema']:
            ltype = schema['schema'][line]['type']
            required = ''
            if 'required' in schema['schema'][line]:
                if schema['schema'][line]['required']:
                    required = 'True'
            default = ''
            if 'default' in schema['schema'][line]:
                default = schema['schema'][line]['default']
            data_relation = ''
            if schema['schema'][line]['type'] == 'objectid':
                data_relation = ":ref:`%s <resource-%s>`" % (schema['schema'][line]['data_relation']['resource'], schema['schema'][line]['data_relation']['resource'])
                relations[schema['schema'][line]['data_relation']['resource']] = required
            if schema['schema'][line]['type'] == 'list':
                if 'schema' in schema['schema'][line] and 'data_relation' in schema['schema'][line]['schema']:
                    data_relation = ":ref:`%s <resource-%s>`" % (schema['schema'][line]['schema']['data_relation']['resource'], schema['schema'][line]['schema']['data_relation']['resource'])
                    relations[schema['schema'][line]['schema']['data_relation']['resource']] = required
                    ltype += " of objectid"

            if required == 'True':
                target.write("   \"**%s**\", \"**%s**\", \"**%s**\", \"**%s**\", \"%s\"\n" % (line, ltype, required, default, data_relation))
            else:
                target.write("   \"%s\", \"%s\", \"%s\", \"%s\", \"%s\"\n" % (line, ltype, required, default, data_relation))
        generate_relation_graph(py_mod.get_name(), relations, resource_name)
        target.write("\n")
        target.close()
