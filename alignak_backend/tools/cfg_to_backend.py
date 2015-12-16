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

"""
Usage:
    {command} [-h] [-v] [-d] [-b=url] [-u=username] [-p=password] [<cfg_file>...]

Options:
    -h, --help                  Show this screen.
    -v, --version               Show application version.
    -b, --backend url           Specify backend URL [default: http://127.0.0.1:5000]
    -d, --delete                Delete existing backend data
    -u, --username username     Backend login username [default: admin]
    -p, --password password     Backend login password [default: admin]

Use cases:
    Display help message:
        {command} -h
    Display current version:
        {command} -v

    Delete current backend data:
        {command} -d [-b=backend] [-u=username] [-p=password]

    Add some data in current backend:
        {command} [-b=backend] [-u=username] [-p=password] <cfg_file>

    Replace current backend data:
        {command} -d [-b=backend] [-u=username] [-p=password] <cfg_file>

    Exit code:
        0 if required operation succeeded
        1 if Alignak is not installed
        2 if backend access is denied (check provided username/password)
        3 if required configuration cannot be loaded
        64 if command line parameters are not used correctly

"""
from __future__ import print_function
import re
from future.utils import iteritems
from docopt import docopt
from docopt import DocoptExit

from alignak_backend_client.client import Backend, BackendException
try:
    from alignak.daemons.arbiterdaemon import Arbiter
    from alignak.objects.item import Item
    from alignak.objects.config import Config
    import alignak.daterange as daterange
except ImportError:
    print("Alignak is not installed...")
    exit(1)

from alignak_backend.models import command
from alignak_backend.models import timeperiod
from alignak_backend.models import hostgroup
from alignak_backend.models import hostdependency
from alignak_backend.models import servicedependency
from alignak_backend.models import serviceextinfo
from alignak_backend.models import trigger
from alignak_backend.models import contact
from alignak_backend.models import contactgroup
from alignak_backend.models import contactrestrictrole
from alignak_backend.models import escalation
from alignak_backend.models import host
from alignak_backend.models import hostextinfo
from alignak_backend.models import hostescalation
from alignak_backend.models import servicegroup
from alignak_backend.models import service
from alignak_backend.models import serviceescalation


def main():
    """
    Main function
    """
    # Store list of errors found
    errors_found = []

    # Get command line parameters
    try:
        args = docopt(__doc__, version='0.2.0')
    except DocoptExit:
        print("Command line parsing error")
        exit(64)

    # Define here the path of the cfg files
    cfg = None
    if '<cfg_file>' in args:
        cfg = args['<cfg_file>']
        print ("Configuration to load: %s" % cfg)
    else:
        print ("No configuration specified")

    # Define here the url of the backend
    backend_url = args['--backend']
    print ("Backend URL: %s", backend_url)

    # Delete all objects in backend ?
    destroy_backend_data = args['--delete']
    print ("Delete existing backend data: %s" % destroy_backend_data)

    username = args['--username']
    password = args['--password']
    print ("Backend login with credentials: %s/%s" % (username, password))

    def check_mapping(items, mapping):
        """
        Check if elements are found ...
        """
        response = {
            'all_found': True,
            'data': items
        }
        new_list = []
        for item in items:
            if item in mapping:
                new_list.append(mapping[item])
            else:
                response['all_found'] = False
        if response['all_found']:
            response['data'] = new_list
        return response

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Backend authentication ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # Backend authentication with token generation
    headers = {'Content-Type': 'application/json'}
    payload = {'username': username, 'password': password, 'action': 'generate'}
    backend = Backend(backend_url)
    backend.login(username, password)

    if backend.token is None:
        print("Access denied!")
        exit(2)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Authenticated ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    # Destroy data in backend if defined
    if destroy_backend_data:
        print("~~~~~~~~~~~~~~~~~~~~~~~~ Deleting existing backend data ~~~~~~~~~~~~~~~~~~~~~~~~~~")
        headers = {'Content-Type': 'application/json'}
        backend.delete('command', headers)
        backend.delete('timeperiod', headers)
        backend.delete('hostgroup', headers)
        backend.delete('hostdependency', headers)
        backend.delete('servicedependency', headers)
        backend.delete('serviceextinfo', headers)
        backend.delete('trigger', headers)
        contacts = backend.get_all('contact')
        headers_contact = {'Content-Type': 'application/json'}
        for cont in contacts:
            if cont['name'] != 'admin':
                headers_contact['If-Match'] = cont['_etag']
                backend.delete('contact/' + cont['_id'], headers_contact)
        backend.delete('contactgroup', headers)
        backend.delete('contactrestrictrole', headers)
        backend.delete('escalation', headers)
        backend.delete('host', headers)
        backend.delete('hostextinfo', headers)
        backend.delete('hostescalation', headers)
        backend.delete('servicegroup', headers)
        backend.delete('service', headers)
        backend.delete('serviceescalation', headers)
        backend.delete('livestate', headers)
        backend.delete('livesynthesis', headers)
        print("~~~~~~~~~~~~~~~~~~~~~~~~ Existing backend data destroyed ~~~~~~~~~~~~~~~~~~~~~~~~~")

    if not cfg:
        print ("No configuration specified")
        exit(2)

    if not isinstance(cfg, list):
        cfg = [cfg]

    # Get flat files configuration
    try:
        arbiter = Arbiter(cfg, False, False, False, False, '')
        arbiter.load_config_file()

        # Load only conf file for timeperiod.dateranges
        alconf = Config()
        buf = alconf.read_config(cfg)
        raw_objects = alconf.read_config_buf(buf)

    except Exception as e:
        print("Configuration loading exception: %s" % str(e))
        exit(3)

    def recompose_dateranges():
        """
        For each timeperiod, recompose daterange in backend format

        :return: None
        """
        # modify dateranges of timeperiods
        fields = ['imported_from', 'use', 'name', 'definition_order', 'register',
                  'timeperiod_name', 'alias', 'dateranges', 'exclude', 'is_active']
        for ti in raw_objects['timeperiod']:
            dateranges = []
            for propti in ti:
                if propti not in fields:
                    dateranges.append({propti: ','.join(ti[propti])})
            ti['dr'] = dateranges

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Order of objects + fields to update post add
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    # COMMAND
    # TIMEPERIOD
    # HOSTGROUP
    #    hostgroup.hostgroup_members
    # HOSTDEPENDENCY
    # SERVICEDEPENDENCY
    # SERVICEEXTINFO
    # TRIGGER
    # CONTACT
    # CONTACTGROUP
    #    contact.contactgroups / contactgroup.contactgroup_members
    # CONTACTRESTRICTROLE
    # ESCALATION
    # HOST
    #    hostgroup.members / host.use / host.parents
    # HOSTEXTINFO
    # HOSTESCALATION
    # SERVICEGROUP
    #    servicegroup.servicegroup_members
    # SERVICE
    # SERVICEESCALATION
    #

    def convert_objects(source):
        """
        Convert objects in name of this object

        :param source: object properties
        :type source: dict
        :return: properties modified
        :rtype: dict
        """
        names = ['service_description', 'host_name', 'command_name', 'timeperiod_name']
        addprop = {}
        for prop in source:
            if 'alignak.commandcall.CommandCall' in str(type(source[prop])):
                if prop == 'check_command':
                    addprop['check_command_args'] = getattr(source[prop], 'args')
                source[prop] = getattr(source[prop], 'command')

            if prop == 'dateranges':
                for ti in raw_objects['timeperiod']:
                    if ti['timeperiod_name'][0] == source['timeperiod_name']:
                        source[prop] = ti['dr']
            elif isinstance(source[prop], list) and source[prop] and isinstance(source[prop][0],
                                                                                Item):
                elements = []
                for element in source[prop]:
                    for name in names:
                        if hasattr(element, name):
                            print('Found %s in prop %s' % (name, prop))
                            elements.append(getattr(element, name))
                            break
                source[prop] = elements
            elif isinstance(source[prop], Item):
                for name in names:
                    if hasattr(source[prop], name):
                        print('Found %s in prop %s' % (name, prop))
                        source[prop] = getattr(source[prop], name)
                        break
            elif isinstance(source[prop], object):
                print("vvvvvvvvvvvvvvvvvvvvvvv")
                print(prop)
                print(dir(source[prop]))
                print(source[prop])
                print(source[prop].notificationway_name)

        source.update(addprop)
        print('***********************************************')
        print(source)
        return source

    def update_later(later, inserted, resource, field, schema):
        """
        Update field of resource having a link with other resources (objectid in backend)

        :param later:
        :type later: dict
        :param inserted:
        :type inserted: dict
        :param resource: resource name (command, contact, host...)
        :type resource: str
        :param field: field of resource to update
        :type field: str
        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        for (index, item) in iteritems(later[resource][field]):
            if item['type'] == 'simple':
                data = {field: inserted[item['resource']][item['value']]}
            elif item['type'] == 'list':
                data = {field: []}
                for val in item['value']:
                    val = val.strip()
                    if val not in inserted[item['resource']]:
                        errors_found.append("# Unknown %s: %s for %s" % (item['resource'],
                                                                         val, resource))
                    else:
                        data[field].append(inserted[item['resource']][val])

            headers['If-Match'] = item['_etag']
            print("before_patch: %s : %s:" % (''.join([resource, '/', index]), data))
            resp = backend.patch(''.join([resource, '/', index]), data, headers, True)
            if '_status' in resp:
                if resp['_status'] == 'ERR':
                    raise ValueError(resp['_issues'])
                elif resp['_status'] == 'OK':
                    for (ind, it) in iteritems(later[resource]):
                        if index in later[resource][ind]:
                            later[resource][ind][index]['_etag'] = resp['_etag']

    def manage_resource(r_name, inserted, later, data_later, id_name, schema):
        """

        data_later = [{'field': 'use', 'type': 'simple|list', 'resource': 'command'}]

        :param r_name: resource name
        :type r_name: str
        :param inserted:
        :param later:
        :param data_later:
        :param id_name:
        :param schema:
        :return:
        """
        if r_name not in inserted:
            inserted[r_name] = {}
        if r_name not in later:
            later[r_name] = {}
        for k, values in enumerate(data_later):
            if values['field'] not in later[r_name]:
                later[r_name][values['field']] = {}
        alignak_resource = r_name + 's'
        if re.search('y$', r_name):
            alignak_resource = re.sub('y$', 'ies', r_name)
        elif r_name == 'hostextinfo':
            alignak_resource = 'hostsextinfo'
        elif r_name == 'serviceextinfo':
            alignak_resource = 'servicesextinfo'

        for item_obj in getattr(arbiter.conf, alignak_resource):
            item = {}
            for prop in item_obj.properties.keys():
                if not hasattr(item_obj, prop):
                    continue
                item[prop] = getattr(item_obj, prop)

            if item[id_name] in ['bp_rule', '_internal_host_up', '_echo']:
                continue
            # convert objects
            item = convert_objects(item)
            # Remove properties
            prop_to_del = []
            for prop in item:
                if item[prop] is None:
                    prop_to_del.append(prop)
                elif prop == 'register':
                    prop_to_del.append(prop)
                elif prop == '_id':
                    prop_to_del.append(prop)
                if isinstance(item[prop], list) and len(item[prop]) == 1:
                    # case we have [''], rewrite it to []
                    if item[prop][0] == '':
                        del item[prop][0]
            for prop in prop_to_del:
                del item[prop]
            later_tmp = {}
            headers = {
                'Content-Type': 'application/json',
            }
            if 'imported_from' in item:
                del item['imported_from']

            # Fred
            # Special case of contacts
            if r_name == 'contact':
                if 'contact_name' in item:
                    if item['contact_name'] == "admin":
                        break
                    # else:
                        # item['back_role_super_admin'] = False
                        # item['back_role_admin'] = False

            # Hack for check_command_args
            if 'check_command_args' in item:
                if isinstance(item['check_command_args'], list):
                    item['check_command_args'] = '!'.join(item['check_command_args'])
            for k, values in enumerate(data_later):
                # {'field': 'hostgroups', 'type': 'list', 'resource': 'hostgroup'},
                if values['field'] in item:
                    if values['type'] == 'simple':
                        if values['now'] \
                                and values['resource'] in inserted \
                                and item[values['field']] in inserted[values['resource']]:
                            item[values['field']] = inserted[
                                values['resource']
                            ][item[values['field']]]
                        else:
                            later_tmp[values['field']] = item[values['field']]
                            del item[values['field']]
                    elif values['type'] == 'list':
                        add = True
                        objectsid = []
                        if values['now']:
                            if isinstance(item[values['field']], basestring):
                                item[values['field']] = item[values['field']].split()
                            for keylist, vallist in enumerate(item[values['field']]):
                                vallist = vallist.strip()
                                if values['resource'] in inserted:
                                    if vallist in inserted[values['resource']]:
                                        objectsid.append(inserted[values['resource']][vallist])
                                else:
                                    add = False
                        else:
                            add = False
                        if add:
                            item[values['field']] = objectsid
                        else:
                            later_tmp[values['field']] = item[values['field']]
                            del item[values['field']]
            # Special case of contacts
            if r_name == 'contact':
                item['back_role_super_admin'] = False
                item['back_role_admin'] = []

            item['name'] = item[id_name]
            del item[id_name]
            if 'use' in item:
                del item['use']
            # Case where no realm but alignak define internal realm name 'Default'
            if 'realm' in item:
                if item['realm'] == 'Default':
                    del item['realm']
            print("before_post: %s : %s:" % (r_name, item))
            try:
                response = backend.post(r_name, item, headers)
            except BackendException as e:
                print("***** Exception: %s" % str(e))
                if "_issues" in e.response:
                    print("ERROR: %s" % e.response['_issues'])
                errors_found.append("# Post error for: %s : %s" %
                                    (r_name, item))
                errors_found.append("  Issues: %s" %
                                    (e.response['_issues']))
            else:
                print("POST response : %s:" % (response))
                if id_name in item:
                    inserted[r_name][item[id_name]] = response['_id']
                else:
                    inserted[r_name][item['name']] = response['_id']
                for k, values in enumerate(data_later):
                    if values['field'] in later_tmp:
                        later[r_name][values['field']][response['_id']] = {
                            'type': values['type'],
                            'resource': values['resource'],
                            'value': later_tmp[values['field']],
                            '_etag': response['_etag']
                        }

    recompose_dateranges()

    later = {}
    inserted = {}

    print("~~~~~~~~~~~~~~~~~~~~~~ add commands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = []
    schema = command.get_schema()
    manage_resource('command', inserted, later, data_later, 'command_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post commands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    print("~~~~~~~~~~~~~~~~~~~~~~ add timeperiods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = []
    schema = timeperiod.get_schema()
    manage_resource('timeperiod', inserted, later, data_later, 'timeperiod_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post timeperiods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    print("~~~~~~~~~~~~~~~~~~~~~~ add hostdependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = []
    schema = hostdependency.get_schema()
    manage_resource('hostdependency', inserted, later, data_later, 'name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post hostdependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    print("~~~~~~~~~~~~~~~~~~~~~~ add servicedependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = []
    schema = servicedependency.get_schema()
    manage_resource('servicedependency', inserted, later, data_later, 'name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post servicedependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    print("~~~~~~~~~~~~~~~~~~~~~~ add trigger ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = []
    schema = trigger.get_schema()
    manage_resource('trigger', inserted, later, data_later, 'trigger_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post trigger ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    # Fred: no contacts imported ???
    print("~~~~~~~~~~~~~~~~~~~~~~ add contact ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {
            'field': 'contactgroups', 'type': 'list', 'resource': 'contactgroup', 'now': False
        },
        {
            'field': 'host_notification_period', 'type': 'simple', 'resource': 'timeperiod',
            'now': False
        },
        {
            'field': 'service_notification_period', 'type': 'simple', 'resource': 'timeperiod',
            'now': False
        },
        {
            'field': 'host_notification_commands', 'type': 'list', 'resource': 'command',
            'now': False
        },
        {
            'field': 'service_notification_commands', 'type': 'list', 'resource': 'command',
            'now': False
        }
    ]
    schema = contact.get_schema()
    manage_resource('contact', inserted, later, data_later, 'contact_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post contact ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'contact', 'host_notification_period', schema)
    update_later(later, inserted, 'contact', 'service_notification_period', schema)
    update_later(later, inserted, 'contact', 'host_notification_commands', schema)
    update_later(later, inserted, 'contact', 'service_notification_commands', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add contactgroup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'members', 'type': 'list', 'resource': 'contact', 'now': False},
        {'field': 'contactgroup_members', 'type': 'list', 'resource': 'contactgroup', 'now': False}
    ]
    schema = contactgroup.get_schema()
    manage_resource('contactgroup', inserted, later, data_later, 'contactgroup_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post contactgroup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'contactgroup', 'members', schema)
    update_later(later, inserted, 'contactgroup', 'contactgroup_members', schema)
    # update_later(later, inserted, 'contact', 'contactgroups', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add escalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'contacts', 'type': 'list', 'resource': 'contact', 'now': False},
        {'field': 'contact_groups', 'type': 'list', 'resource': 'contactgroup', 'now': True}
    ]
    schema = escalation.get_schema()
    manage_resource('escalation', inserted, later, data_later, 'escalation_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post escalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # update_later(later, inserted, 'escalation', 'contacts', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add hostgroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'members', 'type': 'list', 'resource': 'host', 'now': False},
        {'field': 'hostgroup_members', 'type': 'list', 'resource': 'hostgroup', 'now': False}
    ]
    schema = hostgroup.get_schema()
    manage_resource('hostgroup', inserted, later, data_later, 'hostgroup_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post hostgroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'hostgroup', 'hostgroup_members', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add host ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'parents', 'type': 'list', 'resource': 'host', 'now': False},
        {'field': 'hostgroups', 'type': 'list', 'resource': 'hostgroup', 'now': True},
        {'field': 'check_command', 'type': 'simple', 'resource': 'command', 'now': True},
        {'field': 'check_period', 'type': 'simple', 'resource': 'timeperiod', 'now': True},
        {'field': 'contacts', 'type': 'list', 'resource': 'contact', 'now': False},
        {'field': 'contact_groups', 'type': 'list', 'resource': 'contactgroup', 'now': True},
        {'field': 'notification_period', 'type': 'simple', 'resource': 'timeperiod', 'now': True},
        {'field': 'escalations', 'type': 'list', 'resource': 'escalation', 'now': True}
    ]
    schema = host.get_schema()
    manage_resource('host', inserted, later, data_later, 'host_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post host ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'host', 'parents', schema)
    # update_later(later, inserted, 'host', 'contacts', schema)
    update_later(later, inserted, 'hostgroup', 'members', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add hostextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = []
    schema = hostextinfo.get_schema()
    manage_resource('hostextinfo', inserted, later, data_later, 'host_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post hostextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    print("~~~~~~~~~~~~~~~~~~~~~~ add hostescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'contacts', 'type': 'list', 'resource': 'contact', 'now': False},
        {'field': 'contact_groups', 'type': 'list', 'resource': 'contactgroup', 'now': True}
    ]
    schema = hostescalation.get_schema()
    manage_resource('hostescalation', inserted, later, data_later, 'host_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post hostescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # update_later(later, inserted, 'hostescalation', 'contacts', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add servicegroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'members', 'type': 'list', 'resource': 'service', 'now': False},
        {'field': 'servicegroup_members', 'type': 'list', 'resource': 'servicegroup', 'now': False}
    ]
    schema = servicegroup.get_schema()
    manage_resource('servicegroup', inserted, later, data_later, 'servicegroup_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post servicegroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'servicegroup', 'servicegroup_members', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add service ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'host_name', 'type': 'simple', 'resource': 'host', 'now': True},
        {'field': 'servicegroups', 'type': 'list', 'resource': 'servicegroup', 'now': True},
        {'field': 'check_command', 'type': 'simple', 'resource': 'command', 'now': True},
        {'field': 'check_period', 'type': 'simple', 'resource': 'timeperiod', 'now': True},
        {'field': 'notification_period', 'type': 'simple', 'resource': 'timeperiod', 'now': True},
        {'field': 'contacts', 'type': 'list', 'resource': 'contact', 'now': False},
        {'field': 'contact_groups', 'type': 'list', 'resource': 'contactgroup', 'now': True},
        {'field': 'escalations', 'type': 'list', 'resource': 'escalation', 'now': True},
        {'field': 'maintenance_period', 'type': 'simple', 'resource': 'timeperiod', 'now': True},
        {'field': 'service_dependencies', 'type': 'list', 'resource': 'service', 'now': True}
    ]
    schema = service.get_schema()
    manage_resource('service', inserted, later, data_later, 'service_description', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post service ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # update_later(later, inserted, 'service', 'contacts', schema)
    update_later(later, inserted, 'servicegroup', 'members', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add serviceextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = []
    schema = serviceextinfo.get_schema()
    manage_resource('serviceextinfo', inserted, later, data_later, 'name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post serviceextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    print("~~~~~~~~~~~~~~~~~~~~~~ add serviceescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'contacts', 'type': 'list', 'resource': 'contact', 'now': False},
        {'field': 'contact_groups', 'type': 'list', 'resource': 'contactgroup', 'now': True}
    ]
    schema = serviceescalation.get_schema()
    manage_resource('serviceescalation', inserted, later, data_later, 'host_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post serviceescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # update_later(later, inserted, 'serviceescalation', 'contacts', schema)

    # print all errors found
    print('################################## errors report ##################################')
    for error in errors_found:
        print(error)
    print('###################################################################################')


if __name__ == "__main__":  # pragma: no cover
    main()
