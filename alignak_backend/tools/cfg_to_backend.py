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
    -V, --version               Show application version.
    -b, --backend url           Specify backend URL [default: http://127.0.0.1:5000]
    -d, --delete                Delete existing backend data
    -u, --username username     Backend login username [default: admin]
    -p, --password password     Backend login password [default: admin]
    -v, --verbose               Run in verbose mode (more info to display)

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


class CfgToBackend(object):
    """
    Class to manage an item
    An Item is the base of many objects of Alignak. So it define common properties,
    common functions.
    """

    # Store list of errors found
    errors_found = []

    def __init__(self):

        self.later = {}
        self.inserted = {}

        # Get command line parameters
        try:
            args = docopt(__doc__, version='0.2.0')
        except DocoptExit:
            print("Command line parsing error")
            exit(64)

        # Verbose
        self.verbose = False
        if '--verbose' in args:
            self.verbose = True

        # Define here the path of the cfg files
        cfg = None
        if '<cfg_file>' in args:
            cfg = args['<cfg_file>']
            self.log("Configuration to load: %s" % cfg)
        else:
            self.log("No configuration specified")

        # Define here the url of the backend
        self.backend_url = args['--backend']
        self.log("Backend URL: %s" % self.backend_url)

        # Delete all objects in backend ?
        self.destroy_backend_data = args['--delete']
        self.log("Delete existing backend data: %s" % self.destroy_backend_data)

        self.username = args['--username']
        self.password = args['--password']
        self.log("Backend login with credentials: %s/%s" % (self.username, self.password))

        # Authenticate on Backend
        self.authenticate()
        # Delete data in backend if asked in arguments
        self.delete_data()

        # get realm id
        self.realm_all = ''
        realms = self.backend.get_all('realm')
        for cont in realms:
            if cont['name'] == 'All' and cont['_level'] == 0:
                self.realm_all = cont['_id']

        if not cfg:
            print("No configuration specified")
            exit(2)

        if not isinstance(cfg, list):
            cfg = [cfg]

        # Get flat files configuration
        try:
            self.arbiter = Arbiter(cfg, False, False, False, False, '')
            self.arbiter.load_config_file()

            # Load only conf file for timeperiod.dateranges
            alconf = Config()
            buf = alconf.read_config(cfg)
            self.raw_objects = alconf.read_config_buf(buf)

        except Exception as e:
            print("Configuration loading exception: %s" % str(e))
            exit(3)

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

        self.recompose_dateranges()
        self.import_objects()
        # print all errors found
        print('################################## errors report ##################################')
        for error in self.errors_found:
            print(error)
        print('###################################################################################')

    def authenticate(self):
        """
        Login on backend with username and password

        :return: None
        """
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Backend authentication ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # Backend authentication with token generation
        headers = {'Content-Type': 'application/json'}
        payload = {'username': self.username, 'password': self.password, 'action': 'generate'}
        self.backend = Backend(self.backend_url)
        self.backend.login(self.username, self.password)

        if self.backend.token is None:
            print("Access denied!")
            exit(2)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Authenticated ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    def delete_data(self):
        """
        Delete data in backend

        :return: None
        """
        if self.destroy_backend_data:
            print("~~~~~~~~~~~~~~~~~~~~~~~~ Deleting existing backend data ~~~~~~~~~~~~~~~~~~~~~~")
            headers = {'Content-Type': 'application/json'}
            self.backend.delete('command', headers)
            self.backend.delete('timeperiod', headers)
            self.backend.delete('hostgroup', headers)
            self.backend.delete('hostdependency', headers)
            self.backend.delete('servicedependency', headers)
            self.backend.delete('serviceextinfo', headers)
            self.backend.delete('trigger', headers)
            contacts = self.backend.get_all('contact')
            headers_contact = {'Content-Type': 'application/json'}
            for cont in contacts:
                if cont['name'] != 'admin':
                    headers_contact['If-Match'] = cont['_etag']
                    self.backend.delete('contact/' + cont['_id'], headers_contact)
            realms = self.backend.get_all('realm')
            headers_realm = {'Content-Type': 'application/json'}
            for cont in realms:
                if cont['name'] != 'All' and cont['_level'] != 0:
                    headers_realm['If-Match'] = cont['_etag']
                    self.backend.delete('realm/' + cont['_id'], headers_realm)
            self.backend.delete('contactgroup', headers)
            self.backend.delete('contactrestrictrole', headers)
            self.backend.delete('escalation', headers)
            self.backend.delete('host', headers)
            self.backend.delete('hostextinfo', headers)
            self.backend.delete('hostescalation', headers)
            self.backend.delete('servicegroup', headers)
            self.backend.delete('service', headers)
            self.backend.delete('serviceescalation', headers)
            self.backend.delete('livestate', headers)
            self.backend.delete('livesynthesis', headers)
            self.log("~~~~~~~~~~~~~~~~~~~~~~~~ Existing backend data destroyed ~~~~~~~~~~~~~~~~~")

    def recompose_dateranges(self):
        """
        For each timeperiod, recompose daterange in backend format

        :return: None
        """
        # modify dateranges of timeperiods
        fields = ['imported_from', 'use', 'name', 'definition_order', 'register',
                  'timeperiod_name', 'alias', 'dateranges', 'exclude', 'is_active']
        for ti in self.raw_objects['timeperiod']:
            dateranges = []
            for propti in ti:
                if propti not in fields:
                    dateranges.append({propti: ','.join(ti[propti])})
            ti['dr'] = dateranges

    def convert_objects(self, source):
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
                for ti in self.raw_objects['timeperiod']:
                    if ti['timeperiod_name'][0] == source['timeperiod_name']:
                        source[prop] = ti['dr']
            elif isinstance(source[prop], list) and source[prop] and isinstance(source[prop][0],
                                                                                Item):
                elements = []
                for element in source[prop]:
                    for name in names:
                        if hasattr(element, name):
                            self.log('Found %s in prop %s' % (name, prop))
                            elements.append(getattr(element, name))
                            break
                source[prop] = elements
            elif isinstance(source[prop], Item):
                for name in names:
                    if hasattr(source[prop], name):
                        self.log('Found %s in prop %s' % (name, prop))
                        source[prop] = getattr(source[prop], name)
                        break
            elif isinstance(source[prop], object):
                self.log("vvvvvvvvvvvvvvvvvvvvvvv")
                self.log(prop)
                self.log(dir(source[prop]))
                self.log(source[prop])

        source.update(addprop)
        self.log('***********************************************')
        self.log(source)
        return source

    def update_later(self, resource, field, schema):
        """
        Update field of resource having a link with other resources (objectid in backend)

        :param resource: resource name (command, contact, host...)
        :type resource: str
        :param field: field of resource to update
        :type field: str
        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        for (index, item) in iteritems(self.later[resource][field]):
            if item['type'] == 'simple':
                data = {field: self.inserted[item['resource']][item['value']]}
            elif item['type'] == 'list':
                data = {field: []}
                for val in item['value']:
                    val = val.strip()
                    if val not in self.inserted[item['resource']]:
                        self.errors_found.append("# Unknown %s: %s for %s" % (item['resource'],
                                                                              val, resource))
                    else:
                        data[field].append(self.inserted[item['resource']][val])

            headers['If-Match'] = item['_etag']
            self.log("before_patch: %s : %s:" % (''.join([resource, '/', index]), data))
            resp = self.backend.patch(''.join([resource, '/', index]), data, headers, True)
            if '_status' in resp:
                if resp['_status'] == 'ERR':
                    raise ValueError(resp['_issues'])
                elif resp['_status'] == 'OK':
                    for (ind, it) in iteritems(self.later[resource]):
                        if index in self.later[resource][ind]:
                            self.later[resource][ind][index]['_etag'] = resp['_etag']

    def manage_resource(self, r_name, data_later, id_name, schema):
        """

        data_later = [{'field': 'use', 'type': 'simple|list', 'resource': 'command'}]

        :param r_name: resource name
        :type r_name: str
        :param data_later:
        :param id_name:
        :param schema:
        :return:
        """
        if r_name not in self.inserted:
            self.inserted[r_name] = {}
        if r_name not in self.later:
            self.later[r_name] = {}
        for k, values in enumerate(data_later):
            if values['field'] not in self.later[r_name]:
                self.later[r_name][values['field']] = {}
        alignak_resource = r_name + 's'
        if re.search('y$', r_name):
            alignak_resource = re.sub('y$', 'ies', r_name)
        elif r_name == 'hostextinfo':
            alignak_resource = 'hostsextinfo'
        elif r_name == 'serviceextinfo':
            alignak_resource = 'servicesextinfo'

        for item_obj in getattr(self.arbiter.conf, alignak_resource):
            item = {}
            for prop in item_obj.properties.keys():
                if not hasattr(item_obj, prop):
                    continue
                item[prop] = getattr(item_obj, prop)

            if item[id_name] in ['bp_rule', '_internal_host_up', '_echo']:
                continue
            # convert objects
            item = self.convert_objects(item)
            # Remove properties
            prop_to_del = []
            for prop in item:
                if item[prop] is None:
                    prop_to_del.append(prop)
                elif prop == 'register':
                    prop_to_del.append(prop)
                elif prop == '_id':
                    prop_to_del.append(prop)
                elif prop == 'imported_from':
                    prop_to_del.append(prop)
                # case we have [''], rewrite it to []
                elif isinstance(item[prop], list) and len(item[prop]) == 1 and item[prop][0] == '':
                    del item[prop][0]
            for prop in prop_to_del:
                del item[prop]
            later_tmp = {}
            headers = {'Content-Type': 'application/json'}

            # Fred
            # Special case of contacts
            if r_name == 'contact' and 'contact_name' in item and item['contact_name'] == "admin":
                break

            # Hack for check_command_args
            if 'check_command_args' in item and isinstance(item['check_command_args'], list):
                item['check_command_args'] = '!'.join(item['check_command_args'])
            for k, values in enumerate(data_later):
                # {'field': 'hostgroups', 'type': 'list', 'resource': 'hostgroup'},
                if values['field'] in item and values['type'] == 'simple':
                    if values['now'] \
                            and values['resource'] in self.inserted \
                            and item[values['field']] in self.inserted[values['resource']]:
                        item[values['field']] = \
                            self.inserted[values['resource']][item[values['field']]]
                    else:
                        later_tmp[values['field']] = item[values['field']]
                        del item[values['field']]
                elif values['field'] in item and values['type'] == 'list' and values['now']:
                    add = True
                    objectsid = []
                    if isinstance(item[values['field']], basestring):
                        item[values['field']] = item[values['field']].split()
                    for keylist, vallist in enumerate(item[values['field']]):
                        vallist = vallist.strip()
                        if values['resource'] in self.inserted and \
                                vallist in self.inserted[values['resource']]:
                            objectsid.append(self.inserted[values['resource']][vallist])
                        elif values['resource'] in self.inserted:
                            add = True
                        else:
                            add = False
                    if add:
                        item[values['field']] = objectsid
                    else:
                        later_tmp[values['field']] = item[values['field']]
                        del item[values['field']]
                elif values['field'] in item and values['type'] == 'list' and not values['now']:
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
            if r_name in ['host', 'hostgroup']:
                item['realm'] = self.realm_all
            else:
                item['_realm'] = self.realm_all

            self.log("before_post: %s : %s:" % (r_name, item))
            try:
                response = self.backend.post(r_name, item, headers)
            except BackendException as e:
                print("***** Exception: %s" % str(e))
                if "_issues" in e.response:
                    print("ERROR: %s" % e.response['_issues'])
                self.errors_found.append("# Post error for: %s : %s" % (r_name, item))
                self.errors_found.append("  Issues: %s" % (e.response['_issues']))
            else:
                self.log("POST response : %s:" % (response))
                if id_name in item:
                    self.inserted[r_name][item[id_name]] = response['_id']
                else:
                    self.inserted[r_name][item['name']] = response['_id']
                for k, values in enumerate(data_later):
                    if values['field'] in later_tmp:
                        self.later[r_name][values['field']][response['_id']] = {
                            'type': values['type'],
                            'resource': values['resource'],
                            'value': later_tmp[values['field']],
                            '_etag': response['_etag']
                        }

    def import_objects(self):
        """
        Import objects in backend

        :return: None
        """
        print("~~~~~~~~~~~~~~~~~~~~~~ add commands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = []
        schema = command.get_schema()
        self.manage_resource('command', data_later, 'command_name', schema)
        # print("~~~~~~~~~~~~~~~~~~~~~~ post commands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        print("~~~~~~~~~~~~~~~~~~~~~~ add timeperiods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = []
        schema = timeperiod.get_schema()
        self.manage_resource('timeperiod', data_later, 'timeperiod_name', schema)
        # print("~~~~~~~~~~~~~~~~~~~~~~ post timeperiods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        print("~~~~~~~~~~~~~~~~~~~~~~ add hostdependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = []
        schema = hostdependency.get_schema()
        self.manage_resource('hostdependency', data_later, 'name', schema)
        # print("~~~~~~~~~~~~~~~~~~~~~~ post hostdependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        print("~~~~~~~~~~~~~~~~~~~~~~ add servicedependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = []
        schema = servicedependency.get_schema()
        self.manage_resource('servicedependency', data_later, 'name', schema)
        # print("~~~~~~~~~~~~~~~~~~~~~~ post servicedependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        print("~~~~~~~~~~~~~~~~~~~~~~ add trigger ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = []
        schema = trigger.get_schema()
        self.manage_resource('trigger', data_later, 'trigger_name', schema)
        # print("~~~~~~~~~~~~~~~~~~~~~~ post trigger ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

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
        self.manage_resource('contact', data_later, 'contact_name', schema)
        print("~~~~~~~~~~~~~~~~~~~~~~ post contact ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        self.update_later('contact', 'host_notification_period', schema)
        self.update_later('contact', 'service_notification_period', schema)
        self.update_later('contact', 'host_notification_commands', schema)
        self.update_later('contact', 'service_notification_commands', schema)

        print("~~~~~~~~~~~~~~~~~~~~~~ add contactgroup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = [
            {'field': 'members', 'type': 'list', 'resource': 'contact', 'now': False},
            {'field': 'contactgroup_members', 'type': 'list', 'resource': 'contactgroup',
             'now': False}
        ]
        schema = contactgroup.get_schema()
        self.manage_resource('contactgroup', data_later, 'contactgroup_name', schema)
        print("~~~~~~~~~~~~~~~~~~~~~~ post contactgroup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        self.update_later('contactgroup', 'members', schema)
        self.update_later('contactgroup', 'contactgroup_members', schema)
        # update_later(later, inserted, 'contact', 'contactgroups', schema)

        print("~~~~~~~~~~~~~~~~~~~~~~ add escalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = [
            {'field': 'contacts', 'type': 'list', 'resource': 'contact', 'now': False},
            {'field': 'contact_groups', 'type': 'list', 'resource': 'contactgroup', 'now': True}
        ]
        schema = escalation.get_schema()
        self.manage_resource('escalation', data_later, 'escalation_name', schema)
        # print("~~~~~~~~~~~~~~~~~~~~~~ post escalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # update_later(later, inserted, 'escalation', 'contacts', schema)

        print("~~~~~~~~~~~~~~~~~~~~~~ add hostgroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = [
            {'field': 'members', 'type': 'list', 'resource': 'host', 'now': False},
            {'field': 'hostgroup_members', 'type': 'list', 'resource': 'hostgroup', 'now': False}
        ]
        schema = hostgroup.get_schema()
        self.manage_resource('hostgroup', data_later, 'hostgroup_name', schema)
        print("~~~~~~~~~~~~~~~~~~~~~~ post hostgroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        self.update_later('hostgroup', 'hostgroup_members', schema)

        print("~~~~~~~~~~~~~~~~~~~~~~ add host ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = [
            {'field': 'parents', 'type': 'list', 'resource': 'host', 'now': False},
            {'field': 'hostgroups', 'type': 'list', 'resource': 'hostgroup', 'now': True},
            {'field': 'check_command', 'type': 'simple', 'resource': 'command', 'now': True},
            {'field': 'check_period', 'type': 'simple', 'resource': 'timeperiod', 'now': True},
            {'field': 'contacts', 'type': 'list', 'resource': 'contact', 'now': False},
            {'field': 'contact_groups', 'type': 'list', 'resource': 'contactgroup', 'now': True},
            {'field': 'notification_period', 'type': 'simple', 'resource': 'timeperiod',
             'now': True},
            {'field': 'escalations', 'type': 'list', 'resource': 'escalation', 'now': True}
        ]
        schema = host.get_schema()
        self.manage_resource('host', data_later, 'host_name', schema)
        print("~~~~~~~~~~~~~~~~~~~~~~ post host ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        self.update_later('host', 'parents', schema)
        # update_later(later, inserted, 'host', 'contacts', schema)
        self.update_later('hostgroup', 'members', schema)

        print("~~~~~~~~~~~~~~~~~~~~~~ add hostextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = []
        schema = hostextinfo.get_schema()
        self.manage_resource('hostextinfo', data_later, 'host_name', schema)
        # print("~~~~~~~~~~~~~~~~~~~~~~ post hostextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        print("~~~~~~~~~~~~~~~~~~~~~~ add hostescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = [
            {'field': 'contacts', 'type': 'list', 'resource': 'contact', 'now': False},
            {'field': 'contact_groups', 'type': 'list', 'resource': 'contactgroup', 'now': True}
        ]
        schema = hostescalation.get_schema()
        self.manage_resource('hostescalation', data_later, 'host_name', schema)
        # print("~~~~~~~~~~~~~~~~~~~~~~ post hostescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # update_later(later, inserted, 'hostescalation', 'contacts', schema)

        print("~~~~~~~~~~~~~~~~~~~~~~ add servicegroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = [
            {'field': 'members', 'type': 'list', 'resource': 'service', 'now': False},
            {'field': 'servicegroup_members', 'type': 'list', 'resource': 'servicegroup',
             'now': False}
        ]
        schema = servicegroup.get_schema()
        self.manage_resource('servicegroup', data_later, 'servicegroup_name', schema)
        print("~~~~~~~~~~~~~~~~~~~~~~ post servicegroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        self.update_later('servicegroup', 'servicegroup_members', schema)

        print("~~~~~~~~~~~~~~~~~~~~~~ add service ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = [
            {'field': 'host_name', 'type': 'simple', 'resource': 'host', 'now': True},
            {'field': 'servicegroups', 'type': 'list', 'resource': 'servicegroup', 'now': True},
            {'field': 'check_command', 'type': 'simple', 'resource': 'command', 'now': True},
            {'field': 'check_period', 'type': 'simple', 'resource': 'timeperiod', 'now': True},
            {'field': 'notification_period', 'type': 'simple', 'resource': 'timeperiod',
             'now': True},
            {'field': 'contacts', 'type': 'list', 'resource': 'contact', 'now': False},
            {'field': 'contact_groups', 'type': 'list', 'resource': 'contactgroup', 'now': True},
            {'field': 'escalations', 'type': 'list', 'resource': 'escalation', 'now': True},
            {'field': 'maintenance_period', 'type': 'simple', 'resource': 'timeperiod',
             'now': True},
            {'field': 'service_dependencies', 'type': 'list', 'resource': 'service', 'now': True}
        ]
        schema = service.get_schema()
        self.manage_resource('service', data_later, 'service_description', schema)
        print("~~~~~~~~~~~~~~~~~~~~~~ post service ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # update_later(later, inserted, 'service', 'contacts', schema)
        self.update_later('servicegroup', 'members', schema)

        print("~~~~~~~~~~~~~~~~~~~~~~ add serviceextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = []
        schema = serviceextinfo.get_schema()
        self.manage_resource('serviceextinfo', data_later, 'name', schema)
        # print("~~~~~~~~~~~~~~~~~~~~~~ post serviceextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        print("~~~~~~~~~~~~~~~~~~~~~~ add serviceescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        data_later = [
            {'field': 'contacts', 'type': 'list', 'resource': 'contact', 'now': False},
            {'field': 'contact_groups', 'type': 'list', 'resource': 'contactgroup', 'now': True}
        ]
        schema = serviceescalation.get_schema()
        self.manage_resource('serviceescalation', data_later, 'host_name', schema)
        # print("~~~~~~~~~~~~~~~~~~~~~~ post serviceescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # update_later(later, inserted, 'serviceescalation', 'contacts', schema)

    def log(self, message):
        """
        Display message if in verbose mode

        :param message: message to display
        :type message: str
        :return: None
        """
        if self.verbose:
            print(message)

if __name__ == "__main__":  # pragma: no cover
    CfgToBackend()
