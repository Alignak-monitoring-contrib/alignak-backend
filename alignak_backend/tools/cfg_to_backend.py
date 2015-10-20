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
    {command} [-h] [-v] [-d] [-b=backend] [-u=username] [-p=password] <cfg_file> ...
    {command} -h
    {command} -v

Options:
    -h, --help                  Show this screen.
    -v, --version               Show application version.
    -b, --backend url           Specify backend URL [default: http://127.0.0.1:5000]
    -d, --delete                Delete existing backend data
    -u, --username username     Backend login username [default: admin]
    -p, --password password     Backend login password [default: admin]

"""
from __future__ import print_function
from future.utils import iteritems
from docopt import docopt

from alignak.objects.config import Config
from alignak_backend_client.client import Backend, BackendException

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
    # Get command line parameters
    args = docopt(__doc__, version='0.1.0')

    # Define here the path of the cfg files
    cfg = args['<cfg_file>']
    print ("Configuration to load: %s" % cfg)

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


    # Get flat files configuration
    alconfig = Config()
    buf = alconfig.read_config(cfg)
    print ("Configuration: %s" % (buf))
    conf = alconfig.read_config_buf(buf)
    print ("Configuration: %s" % (conf))


    print("~~~~~~~~~~~~~~~~~~~~~~ First authentication to delete previous data ~~~~~~~~~~~~~~~~~~~")
    # Backend authentication with token generation
    headers = {'Content-Type': 'application/json'}
    payload = {'username': username, 'password': password, 'action': 'generate'}
    backend = Backend(backend_url)
    backend.login(username, password)

    if backend.token is None:
        print("Can't authenticated")
        exit()
    print("~~~~~~~~~~~~~~~~~~~~~~ Authenticated ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    # Destroy data in backend if defined
    if destroy_backend_data:
        headers = {'Content-Type': 'application/json'}
        backend.delete('command', headers)
        backend.delete('timeperiod', headers)
        backend.delete('hostgroup', headers)
        backend.delete('hostdependency', headers)
        backend.delete('servicedependency', headers)
        backend.delete('serviceextinfo', headers)
        backend.delete('trigger', headers)
        # backend.delete('contact', headers)
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
        print("~~~~~~~~~~~~~~~~~~~~~~ Data destroyed ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Order of objects + fields to update post add
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    # COMMAND
    #    command.use
    # TIMEPERIOD
    #    timeperiod.use
    # HOSTGROUP
    #    hostgroup.hostgroup_members
    # HOSTDEPENDENCY
    #    hostdependency.use
    # SERVICEDEPENDENCY
    #    servicedependency.use
    # SERVICEEXTINFO
    #    serviceextinfo.use
    # TRIGGER
    #    trigger.use
    # CONTACT
    #    contact.use
    # CONTACTGROUP
    #    contact.contactgroups / contactgroup.contactgroup_members
    # CONTACTRESTRICTROLE
    #
    # ESCALATION
    #    escalation.use
    # HOST
    #    hostgroup.members / host.use / host.parents
    # HOSTEXTINFO
    #    hostextinfo.use
    # HOSTESCALATION
    #    hostescalation.use
    # SERVICEGROUP
    #    servicegroup.servicegroup_members
    # SERVICE
    #    service.use
    # SERVICEESCALATION
    #    serviceescalation.use
    #


    def update_types(source, schema):
        for prop in source:
            source[prop] = ''.join(source[prop])
            if prop in schema:
                # get type
                if schema[prop]['type'] == 'boolean':
                    if source[prop] == '1':
                        source[prop] = True
                    else:
                        source[prop] = False
                elif schema[prop]['type'] == 'list':
                    source[prop] = source[prop].split(',')
                elif schema[prop]['type'] == 'integer':
                    source[prop] = int(source[prop])
        return source


    def update_later(later, inserted, ressource, field, schema):
        """
        Update field of ressource hav link with other ressources (objectid in backend)

        :param later:
        :type later: dict
        :param inserted:
        :type inserted: dict
        :param ressource: ressource name (command, contact, host...)
        :type ressource: str
        :param field: field of ressource to update
        :type field: str
        :return: None
        """
        def get_template(ressource, value):
            """

            :param ressource:
            :param value: value of use
            :return:
            """
            if isinstance(value, basestring):
                value = value.split()
            for template_value in reversed(value):
                template_value = template_value.strip()
                if template_value not in template[ressource]:
                    print ("***** Undeclared template: %s" % template_value)
                    continue
                print ("Template: %s - %s" % (template_value, template[ressource][template_value]))
                if 'use' in template[ressource][template_value]:
                    get_template(ressource, template[ressource][template_value]['use'])
                for key, val in iteritems(template[ressource][template_value]):
                    if key not in ['register', 'name', 'use']:
                        data[key] = val
                    elif key == 'name':
                        if val not in inserted[ressource]:
                            print ("Key/val: %s = %s" % (key, val))
                            print ("Inserted: %s" % (inserted[ressource]))
                            print ("***** Unknown resource: %s" % val)
                            continue
                        data['use'].append(inserted[ressource][val])

        headers = {'Content-Type': 'application/json'}
        for (index, item) in iteritems(later[ressource][field]):
            if field == 'use':
                data = {'use': []}
                get_template(ressource, item['value'])
                # data = update_types(data, schema)
                use_data = []
                for template_id in reversed(data['use']):
                    use_data.append(template_id)
                data['use'] = use_data
            else:
                if item['type'] == 'simple':
                    data = {field: inserted[item['ressource']][item['value']]}
                elif item['type'] == 'list':
                    data = {field: []}
                    for val in item['value']:
                        print ("***** Unknown %s: %s" % (item['ressource'], val))
                        continue
                        data[field].append(inserted[item['ressource']][val.strip()])

            headers['If-Match'] = item['_etag']
            resp = backend.patch(''.join([ressource, '/', index]), data, headers, True)
            if '_status' in resp:
                if resp['_status'] == 'ERR':
                    raise ValueError(resp['_issues'])
                elif resp['_status'] == 'OK':
                    for (ind, it) in iteritems(later[ressource]):
                        if index in later[ressource][ind]:
                            later[ressource][ind][index]['_etag'] = resp['_etag']


    def manage_ressource(r_name, inserted, later, data_later, id_name, schema):
        """

        data_later = [{'field': 'use', 'type': 'simple|list', 'ressource': 'command'}]

        :param r_name:
        :param inserted:
        :param later:
        :param data_later:
        :return:
        """
        if r_name not in inserted:
            inserted[r_name] = {}
        if r_name not in template:
            template[r_name] = {}
        if r_name not in later:
            later[r_name] = {}
        for k, values in enumerate(data_later):
            if values['field'] not in later[r_name]:
                later[r_name][values['field']] = {}
        if r_name in conf:
            for item in conf[r_name]:
                later_tmp = {}
                headers = {
                    'Content-Type': 'application/json',
                }
                if 'imported_from' in item:
                    del item['imported_from']
                for p in item:
                    item[p] = item[p][0]
                # Hack for check_command_args
                if r_name in ['host', 'service']:
                    if 'check_command' in item:
                        commands = item['check_command'].split('!', 1)
                        item['check_command'] = commands[0]
                        if len(commands) == 2:
                            item['check_command_args'] = commands[1]

                # convert type (boolean, integer...)
                item = update_types(item, schema['schema'])
                for k, values in enumerate(data_later):
                    # {'field': 'hostgroups', 'type': 'list', 'ressource': 'hostgroup'},
                    if values['field'] in item:
                        if values['type'] == 'simple':
                            if values['now'] \
                                    and values['ressource'] in inserted \
                                    and item[values['field']] in inserted[values['ressource']]:
                                item[values['field']] = inserted[
                                    values['ressource']
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
                                    if values['ressource'] in inserted:
                                        if vallist in inserted[values['ressource']]:
                                            objectsid.append(inserted[values['ressource']][vallist])
                                    else:
                                        add = False
                            else:
                                add = False
                            if add:
                                item[values['field']] = objectsid
                            else:
                                later_tmp[values['field']] = item[values['field']]
                                del item[values['field']]

                # special case of timeperiod
                if r_name == 'timeperiod':
                    fields = ['imported_from', 'use', 'name', 'definition_order', 'register',
                              'timeperiod_name', 'alias', 'dateranges', 'exclude', 'is_active']
                    item['dateranges'] = []
                    prop_to_del = []
                    for prop in item:
                        if prop not in fields:
                            item['dateranges'].append({prop: item[prop]})
                            prop_to_del.append(prop)
                    for prop in prop_to_del:
                        del item[prop]
                # if template add to template
                if 'register' in item:
                    if not item['register']:
                        # print("***** Template: %s" % item)
                        if 'name' in item:
                            template[r_name][item['name']] = item.copy()
                        else:
                            print("***** Missing name property in template: %s" % item)
                            if 'service_description' in item:
                                item['name'] = item['service_description']
                                template[r_name][item['name']] = item.copy()
                            elif 'host_name' in item:
                                item['name'] = item['host_name']
                                template[r_name][item['name']] = item.copy()
                print("before_post")
                print("%s : %s:" % (r_name, item))
                try:
                    response = backend.post(r_name, item, headers)
                except BackendException as e:
                    print("***** Exception: %s" % str(e))
                    if "_issues" in e.response:
                        print("ERROR: %s" % e.response['_issues'])
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
                                'ressource': values['ressource'],
                                'value': later_tmp[values['field']],
                                '_etag': response['_etag']
                            }

    later = {}
    inserted = {}
    template = {}

    print("~~~~~~~~~~~~~~~~~~~~~~ add commands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [{'field': 'use', 'type': 'list', 'ressource': 'command', 'now': False}]
    schema = command.get_schema()
    manage_ressource('command', inserted, later, data_later, 'command_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post commands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'command', 'use', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add timeperiods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [{'field': 'use', 'type': 'list', 'ressource': 'timeperiod', 'now': False}]
    schema = timeperiod.get_schema()
    manage_ressource('timeperiod', inserted, later, data_later, 'timeperiod_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post timeperiods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'timeperiod', 'use', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add hostgroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {
            'field': 'members', 'type': 'list', 'ressource': 'host', 'now': False
        },
        {
            'field': 'hostgroup_members', 'type': 'list', 'ressource': 'hostgroup', 'now': False
        }
    ]
    schema = hostgroup.get_schema()
    manage_ressource('hostgroup', inserted, later, data_later, 'hostgroup_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post hostgroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'hostgroup', 'hostgroup_members', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add hostdependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [{'field': 'use', 'type': 'list', 'ressource': 'hostdependency', 'now': False}]
    schema = hostdependency.get_schema()
    manage_ressource('hostdependency', inserted, later, data_later, 'name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post hostdependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'hostdependency', 'use', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add servicedependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [{'field': 'use', 'type': 'list', 'ressource': 'servicedependency', 'now': False}]
    schema = servicedependency.get_schema()
    manage_ressource('servicedependency', inserted, later, data_later, 'name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post servicedependency ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'servicedependency', 'use', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add serviceextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [{'field': 'use', 'type': 'list', 'ressource': 'serviceextinfo', 'now': False}]
    schema = serviceextinfo.get_schema()
    manage_ressource('serviceextinfo', inserted, later, data_later, 'name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post serviceextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'serviceextinfo', 'use', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add trigger ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [{'field': 'use', 'type': 'list', 'ressource': 'trigger', 'now': False}]
    schema = trigger.get_schema()
    manage_ressource('trigger', inserted, later, data_later, 'trigger_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post trigger ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'trigger', 'use', schema)

    # print("~~~~~~~~~~~~~~~~~~~~~~ add contact ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # data_later = [
    # {'field': 'use', 'type': 'simple', 'ressource': 'contact'},
    # {'field': 'contactgroups', 'type': 'list', 'ressource': 'contactgroup'},
    # {'field': 'host_notification_period', 'type': 'simple', 'ressource': 'timeperiod'},
    # {'field': 'service_notification_period', 'type': 'simple', 'ressource': 'timeperiod'},
    # {'field': 'host_notification_commands', 'type': 'list', 'ressource': 'command'},
    # {'field': 'service_notification_commands', 'type': 'list', 'ressource': 'command'}
    # ]
    # schema = contact.get_schema()
    # manage_ressource('contact', inserted, later, data_later, 'contact_name', schema)
    # print("~~~~~~~~~~~~~~~~~~~~~~ post contact ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # update_later(later, inserted, 'contact', 'use', schema)
    # update_later(later, inserted, 'contact', 'host_notification_period', schema)
    # update_later(later, inserted, 'contact', 'service_notification_period', schema)
    # update_later(later, inserted, 'contact', 'host_notification_commands', schema)
    # update_later(later, inserted, 'contact', 'service_notification_commands', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add contactgroup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'members', 'type': 'list', 'ressource': 'contact', 'now': False},
        {'field': 'contactgroup_members', 'type': 'list', 'ressource': 'contactgroup', 'now': False}
    ]
    schema = contactgroup.get_schema()
    manage_ressource('contactgroup', inserted, later, data_later, 'contactgroup_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post contactgroup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # update_later(later, inserted, 'contactgroup', 'members', schema)
    update_later(later, inserted, 'contactgroup', 'contactgroup_members', schema)
    # update_later(later, inserted, 'contact', 'contactgroups', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add contactrestrictrole ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'contact', 'type': 'simple', 'ressource': 'contact', 'now': False}
    ]
    schema = contactrestrictrole.get_schema()
    manage_ressource('contactrestrictrole', inserted, later, data_later, 'contact', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post contactrestrictrole ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # update_later(later, inserted, 'contactrestrictrole', 'contact', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add escalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'use', 'type': 'list', 'ressource': 'escalation', 'now': False},
        {'field': 'contacts', 'type': 'list', 'ressource': 'contact', 'now': False},
        {'field': 'contact_groups', 'type': 'list', 'ressource': 'contactgroup', 'now': True}
    ]
    schema = escalation.get_schema()
    manage_ressource('escalation', inserted, later, data_later, 'escalation_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post escalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'escalation', 'use', schema)
    # update_later(later, inserted, 'escalation', 'contacts', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add host ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'use', 'type': 'list', 'ressource': 'host', 'now': False},
        {'field': 'parents', 'type': 'list', 'ressource': 'host', 'now': False},
        {'field': 'hostgroups', 'type': 'list', 'ressource': 'hostgroup', 'now': True},
        {'field': 'check_command', 'type': 'simple', 'ressource': 'command', 'now': True},
        {'field': 'check_period', 'type': 'simple', 'ressource': 'timeperiod', 'now': True},
        {'field': 'contacts', 'type': 'list', 'ressource': 'contact', 'now': False},
        {'field': 'contact_groups', 'type': 'list', 'ressource': 'contactgroup', 'now': True},
        {'field': 'notification_period', 'type': 'simple', 'ressource': 'timeperiod', 'now': True},
        {'field': 'escalations', 'type': 'list', 'ressource': 'escalation', 'now': True}
    ]
    schema = host.get_schema()
    manage_ressource('host', inserted, later, data_later, 'host_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post host ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'host', 'use', schema)
    update_later(later, inserted, 'host', 'parents', schema)
    # update_later(later, inserted, 'host', 'contacts', schema)
    update_later(later, inserted, 'hostgroup', 'members', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add hostextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [{'field': 'use', 'type': 'list', 'ressource': 'hostextinfo', 'now': False}]
    schema = hostextinfo.get_schema()
    manage_ressource('hostextinfo', inserted, later, data_later, 'host_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post hostextinfo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'hostextinfo', 'use', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add hostescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [{'field': 'use', 'type': 'list', 'ressource': 'hostescalation', 'now': False},
                  {'field': 'contacts', 'type': 'list', 'ressource': 'contact', 'now': False},
                  {'field': 'contact_groups', 'type': 'list', 'ressource': 'contactgroup', 'now': True}]
    schema = hostescalation.get_schema()
    manage_ressource('hostescalation', inserted, later, data_later, 'host_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post hostescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'hostescalation', 'use', schema)
    # update_later(later, inserted, 'hostescalation', 'contacts', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add servicegroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'members', 'type': 'list', 'ressource': 'service', 'now': False},
        {'field': 'servicegroup_members', 'type': 'list', 'ressource': 'servicegroup', 'now': False}
    ]
    schema = servicegroup.get_schema()
    manage_ressource('servicegroup', inserted, later, data_later, 'servicegroup_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post servicegroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'servicegroup', 'servicegroup_members', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add service ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'use', 'type': 'list', 'ressource': 'service', 'now': False},
        {'field': 'host_name', 'type': 'simple', 'ressource': 'host', 'now': True},
        {'field': 'servicegroups', 'type': 'list', 'ressource': 'servicegroup', 'now': True},
        {'field': 'check_command', 'type': 'simple', 'ressource': 'command', 'now': True},
        {'field': 'check_period', 'type': 'simple', 'ressource': 'timeperiod', 'now': True},
        {'field': 'notification_period', 'type': 'simple', 'ressource': 'timeperiod', 'now': True},
        {'field': 'contacts', 'type': 'list', 'ressource': 'contact', 'now': False},
        {'field': 'contact_groups', 'type': 'list', 'ressource': 'contactgroup', 'now': True},
        {'field': 'escalations', 'type': 'list', 'ressource': 'escalation', 'now': True},
        {'field': 'maintenance_period', 'type': 'simple', 'ressource': 'timeperiod', 'now': True},
        {'field': 'service_dependencies', 'type': 'list', 'ressource': 'service', 'now': True}
    ]
    schema = service.get_schema()
    manage_ressource('service', inserted, later, data_later, 'service_description', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post service ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'service', 'use', schema)
    # update_later(later, inserted, 'service', 'contacts', schema)
    update_later(later, inserted, 'servicegroup', 'members', schema)

    print("~~~~~~~~~~~~~~~~~~~~~~ add serviceescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    data_later = [
        {'field': 'use', 'type': 'list', 'ressource': 'serviceescalation', 'now': False},
        {'field': 'contacts', 'type': 'list', 'ressource': 'contact', 'now': False},
        {'field': 'contact_groups', 'type': 'list', 'ressource': 'contactgroup', 'now': True}
    ]
    schema = serviceescalation.get_schema()
    manage_ressource('serviceescalation', inserted, later, data_later, 'host_name', schema)
    print("~~~~~~~~~~~~~~~~~~~~~~ post serviceescalation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    update_later(later, inserted, 'serviceescalation', 'use', schema)
    # update_later(later, inserted, 'serviceescalation', 'contacts', schema)


if __name__ == "__main__":  # pragma: no cover
    main()
