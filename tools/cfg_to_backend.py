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

import requests
from requests.auth import HTTPBasicAuth
import json
import ujson

from alignak.objects.config import Config
from alignak_backend.models.host import get_schema as host_get_schema
from alignak_backend.models.hostgroup import get_schema as hostgroup_get_schema
from alignak_backend.models.contact import get_schema as contact_get_schema
from alignak_backend.models.contactgroup import get_schema as contactgroup_get_schema
from alignak_backend.models.service import get_schema as service_get_schema
from alignak_backend.models.servicegroup import get_schema as servicegroup_get_schema
from alignak_backend.models.timeperiod import get_schema as timeperiod_get_schema

# Define here the path of the cfg files
cfg_path = 'cfg/'

# Define here the url of the backend
backend_url = 'http://localhost:5000/'

# Delete all objects in backend ?
destroy_backend_data = True

username = 'admin'
password = 'admin'
token = None
auth = None

# Don't touch after this line
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def method_post(endpoint, data_json, headers, auth):
    """
    Create a new item

    :param endpoint: endpoint (API URL)
    :type endpoint: str
    :param data_json: properties of item to create
    :type data_json:str
    :param headers: headers (example: Content-Type)
    :type headers: dict
    :return: response (creation information)
    :rtype: dict
    """
    print data_json
    response = requests.post(endpoint, data_json, headers=headers, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        print "%s: %s for %s"  % (response.status_code, response.content, endpoint)
        return response.json()

def method_delete(endpoint, auth):
    response = requests.delete(endpoint, auth=auth)
    print "delete: %d: %s" % (response.status_code, response.text)

def method_patch(endpoint, data_json, headers, auth):
    response = requests.patch(endpoint, data_json, headers=headers, auth=auth)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 412:
        # 412 means Precondition failed
        return response.content
    else:
        print "%s: %s for %s"  % (response.status_code, response.content, endpoint)
        return response.json()


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
    return source


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


alconfig = Config()

file_list = ['cfg/hosts.cfg', 'cfg/commands.cfg', 'cfg/contacts.cfg', 'cfg/hostgroups.cfg',
             'cfg/services.cfg', 'cfg/servicetemplates.cfg', 'cfg/timeperiods.cfg']

buf = alconfig.read_config(file_list)
conf = alconfig.read_config_buf(buf)


print "~~~~~~~~~~~~~~~~~~~~-- First authentication to delete previous data ~~~~~~~~~~~~~~~~~~~~~~~~"
# Backend authentication with token generation
headers = {'Content-Type': 'application/json'}
payload = {'username': username, 'password': password, 'action': 'generate'}
response = requests.post(
    ''.join([backend_url, 'login']),
    json=payload,
    headers=headers
)
response.raise_for_status()
resp = response.json()
token = resp['token']

# Create authentication object and get root endpoint to confirm ...
auth = HTTPBasicAuth(token, '')
response = requests.get(
    ''.join([backend_url, '']),
    auth=auth
)
response.raise_for_status()
resp = response.json()
print "~~~~~~~~~~~~~~~~~~~~-- Authenticated -~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"


# Destroy data in backend if defined
if destroy_backend_data:
    method_delete(''.join([backend_url, 'command']), auth)
    method_delete(''.join([backend_url, 'host']), auth)
    method_delete(''.join([backend_url, 'hostgroup']), auth)
    method_delete(''.join([backend_url, 'service']), auth)
    method_delete(''.join([backend_url, 'timeperiod']), auth)
    # method_delete(''.join([backend_url, 'contact']), auth)


headers = {'content-type': 'application/json'}
commands = {}
hostgroups = {}
hosts = {}
contacts = {}
contactgroups = {}
escalations = {}
timeperiods = {}
services = {}
servicegroups = {}

print "~~~~~~~~~~~~~~~~~~~~-- Second authentication to store new data ~~~~~~~~~~~~~~~~~~~~~~~------"
# Backend authentication with token generation
headers = {'Content-Type': 'application/json'}
payload = {'username': username, 'password': password, 'action': 'generate'}
response = requests.post(
    ''.join([backend_url, 'login']),
    json=payload,
    headers=headers
)
response.raise_for_status()
resp = response.json()
token = resp['token']

# Create authentication object and get root endpoint to confirm ...
auth = HTTPBasicAuth(token, '')
response = requests.get(
    ''.join([backend_url, '']),
    auth=auth
)
response.raise_for_status()
resp = response.json()
print "~~~~~~~~~~~~~~~~~~~~-- Authenticated -~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"


print "~~~~~~~~~~~~~~~~~~~~ Add commands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
for command in conf['command']:
    if 'imported_from' in command:
        del command['imported_from']
    for p in command:
        command[p] = command[p][0]
    response = method_post(''.join([backend_url, 'command']), ujson.dumps(command), headers, auth)
    if '_error' in response and '_issues' in response:
        print "ERROR: %s" % response['_issues']
    else:
        commands[command['command_name']] = response['_id']

print "~~~~~~~~~~~~~~~~~~~~ Add timeperiods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
headers = {'content-type': 'application/json'}
schema = timeperiod_get_schema()
# timeperiod to add later if required
timeperiod_update = {}
for timeperiod in conf['timeperiod']:
    to_update = {}
    timeperiod = update_types(timeperiod, schema['schema'])
    if 'imported_from' in timeperiod:
        del timeperiod['imported_from']
    if 'use' in timeperiod:
        to_update['use'] = timeperiod['use']
        del timeperiod['use']
    fields = ['imported_from', 'use', 'name', 'definition_order', 'register',
              'timeperiod_name', 'alias', 'dateranges', 'exclude', 'is_active']
    timeperiod['dateranges'] = []
    prop_to_del = []
    for prop in timeperiod:
        if prop not in fields:
            timeperiod['dateranges'].append({prop: timeperiod[prop]})
            prop_to_del.append(prop)
    for prop in prop_to_del:
        del timeperiod[prop]
    response = method_post(''.join([backend_url, 'timeperiod']), ujson.dumps(timeperiod), headers, auth)
    if '_error' in response and '_issues' in response:
        print "ERROR: %s" % response['_issues']
    else:
        timeperiods[timeperiod['timeperiod_name']] = response['_id']
        if to_update:
            to_update['_etag'] = response['_etag']
            timeperiod_update[response['_id']] = to_update

print "~~~~~~~~~~~~~~~~~~~~ update 'use' in timeperiods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
id_to_del = []
for id in timeperiod_update:
    if 'use' in timeperiod_update[id]:
        if timeperiod_update[id]['use'] in timeperiods:
            data = {'use': timeperiods[timeperiod_update[id]['use']]}
            headers['If-Match'] = timeperiod_update[id]['_etag']
            response = method_patch(''.join([backend_url, 'timeperiod', '/', id]),
                         ujson.dumps(data), headers, auth)
            timeperiod_update[id]['_etag'] = response['_etag']
            del timeperiod_update[id]['use']
        else:
            print 'ERROR: use timeperiod `%s` not found' % (timeperiod_update[id]['use'])
            del timeperiod_update[id]['use']
        if len(timeperiod_update[id]) == 1:
            id_to_del.append(id)
for id in id_to_del:
    del timeperiod_update[id]

print "~~~~~~~~~~~~~~~~~~~~ Add contactgroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
headers = {'content-type': 'application/json'}
schema = contactgroup_get_schema()
# contactgroup to add later if required
contactgroup_update = {}
for contactgroup in conf['contactgroup']:
    to_update = {}
    contactgroup = update_types(contactgroup, schema['schema'])
    if 'members' in contactgroup:
        to_update['members'] = contactgroup['members']
        del contactgroup['members']
    if 'imported_from' in contactgroup:
        del contactgroup['imported_from']
    if 'contactgroup_members' in contactgroup:
        ret_map = check_mapping(contactgroup['contactgroup_members'], contactgroups)
        if ret_map['all_found']:
            contactgroup['contactgroup_members'] = ret_map['data']
        else:
            to_update['contactgroup_members'] = contactgroup['contactgroup_members']
            del contactgroup['contactgroup_members']
    response = method_post(''.join([backend_url, 'contactgroup']), ujson.dumps(contactgroup), headers, auth)
    if '_error' in response and '_issues' in response:
        print "ERROR: %s" % response['_issues']
    else:
        contactgroups[contactgroup['contactgroup_name']] = response['_id']
        if to_update:
            to_update['_etag'] = response['_etag']
            contactgroup_update[response['_id']] = to_update

print "~~~~~~~~~~~~~~~~~~~~ update 'contactgroup_members' in contactgroups ~~~~~~~~~~~~~~~~~~~~"
id_to_del = []
for id in contactgroup_update:
    new_list = []
    for members in contactgroup_update[id]['contactgroup_members']:
        new_list.append(contactgroups[members])
    data = {'contactgroup_members': new_list}
    headers['If-Match'] = contactgroup_update[id]['_etag']
    response = method_patch(''.join([backend_url, 'contactgroup', '/', id]),
                 ujson.dumps(data), headers, auth)
    contactgroup_update[id]['_etag'] = response['_etag']
    if not 'members' in contactgroup_update[id]:
        id_to_del.append(id)
for id in id_to_del:
    del contactgroup_update[id]

print "~~~~~~~~~~~~~~~~~~~~ Add contact ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
headers = {'content-type': 'application/json'}
schema = contact_get_schema()
# contact to add later if required
contact_update = {}
for contact in conf['contact']:
    to_update = {}
    contact = update_types(contact, schema['schema'])
    # New fields ...
    contact['back_role_super_admin'] = False
    contact['back_role_admin'] = []
    
    if 'imported_from' in contact:
        del contact['imported_from']
    if 'use' in contact:
        to_update['use'] = contact['use']
    if 'host_notification_period' in contact:
        contact['host_notification_period'] = timeperiods[contact['host_notification_period']]
    if 'service_notification_period' in contact:
        contact['service_notification_period'] = timeperiods[contact['service_notification_period']]
    if 'contactgroups' in contact:
        ret_map = check_mapping(contact['contactgroups'], contacts)
        if ret_map['all_found']:
            contact['contactgroups'] = ret_map['data']
        else:
            to_update['contactgroups'] = contact['contactgroups']
            del contact['contactgroups']
    if 'host_notification_commands' in contact:
        ret_map = check_mapping(contact['host_notification_commands'], commands)
        if ret_map['all_found']:
            contact['host_notification_commands'] = ret_map['data']
        else:
            to_update['host_notification_commands'] = contact['host_notification_commands']
            del contact['host_notification_commands']
    if 'service_notification_commands' in contact:
        ret_map = check_mapping(contact['service_notification_commands'], commands)
        if ret_map['all_found']:
            contact['service_notification_commands'] = ret_map['data']
        else:
            to_update['service_notification_commands'] = contact['service_notification_commands']
            del contact['service_notification_commands']
    response = method_post(''.join([backend_url, 'contact']), ujson.dumps(contact), headers, auth)
    if '_error' in response and '_issues' in response:
        print "ERROR: %s" % response['_issues']
        print "Data: %s" % ujson.dumps(contact)
    else:
        contacts[contact['contact_name']] = response['_id']
        if to_update:
            to_update['_etag'] = response['_etag']
            contact_update[response['_id']] = to_update

print "~~~~~~~~~~~~~~~~~~~~ update 'use' in contacts ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
id_to_del = []
for id in contact_update:
    if 'use' in contact_update[id]:
        if contact_update[id]['use'] in contacts:
            data = {'use': contacts[contact_update[id]['use']]}
            headers['If-Match'] = contact_update[id]['_etag']
            response = method_patch(''.join([backend_url, 'contact', '/', id]),
                         ujson.dumps(data), headers, auth)
            contact_update[id]['_etag'] = response['_etag']
            del contact_update[id]['use']
        else:
            print 'ERROR: use contact `%s` not found' % (contact_update[id]['use'])
            del contact_update[id]['use']
        if len(contact_update[id]) == 1:
            id_to_del.append(id)
for id in id_to_del:
    del contact_update[id]

print "~~~~~~~~~~~~~~~~~~~~ Add hostgroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
headers = {'content-type': 'application/json'}
schema = hostgroup_get_schema()
# hostgroup to add later if required
hostgroup_update = {}
for hostgroup in conf['hostgroup']:
    to_update = {}
    hostgroup = update_types(hostgroup, schema['schema'])
    if 'members' in hostgroup:
        to_update['members'] = hostgroup['members']
        del hostgroup['members']
    if 'imported_from' in hostgroup:
        del hostgroup['imported_from']
    if 'hostgroup_members' in hostgroup:
        ret_map = check_mapping(hostgroup['hostgroup_members'], hostgroups)
        if ret_map['all_found']:
            hostgroup['hostgroup_members'] = ret_map['data']
        else:
            to_update['hostgroup_members'] = hostgroup['hostgroup_members']
            del hostgroup['hostgroup_members']
    response = method_post(''.join([backend_url, 'hostgroup']), ujson.dumps(hostgroup), headers, auth)
    if '_error' in response and '_issues' in response:
        print "ERROR: %s" % response['_issues']
    else:
        hostgroups[hostgroup['hostgroup_name']] = response['_id']
        if to_update:
            to_update['_etag'] = response['_etag']
            hostgroup_update[response['_id']] = to_update

print "~~~~~~~~~~~~~~~~~~~~ update 'hostgroup_members' in hostgroups ~~~~~~~~~~~~~~~~~~~~~~~~~~"
id_to_del = []
for id in hostgroup_update:
    new_list = []
    if id not in hostgroup_update:
        print "ERROR: hostgroup id not in hostgroup_update", id
        continue
    if 'hostgroup_members' not in hostgroup_update[id]:
        print "ERROR: hostgroup id not in hostgroup_update", id
        continue
    for members in hostgroup_update[id]['hostgroup_members']:
        new_list.append(hostgroups[members])
    data = {'hostgroup_members': new_list}
    headers['If-Match'] = hostgroup_update[id]['_etag']
    response = method_patch(''.join([backend_url, 'hostgroup', '/', id]),
                 ujson.dumps(data), headers, auth)
    hostgroup_update[id]['_etag'] = response['_etag']
    if not 'members' in hostgroup_update[id]:
        id_to_del.append(id)
for id in id_to_del:
    del hostgroup_update[id]

print "~~~~~~~~~~~~~~~~~~~~ Add hosts ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

headers = {'content-type': 'application/json'}
schema = host_get_schema()
host_update = {}
for host in conf['host']:
    to_update = {}
    host = update_types(host, schema['schema'])
    if 'imported_from' in host:
        del host['imported_from']
    if 'use' in host:
        to_update['use'] = host['use']
        del host['use']
    if 'check_command' in host:
        if '!' in host['check_command']:
            args = host['check_command'].split('!')
            host['check_command'] = args[0]
            del args[0]
            host['check_command_args'] = '!'.join(args)
        host['check_command'] = commands[host['check_command']]
    if 'check_period' in host:
        host['check_period'] = timeperiods[host['check_period']]
    if 'notification_period' in host:
        host['notification_period'] = timeperiods[host['notification_period']]
    relations = {
        'parents': hosts,
        'hostgroups': hostgroups,
        'contacts': contacts,
        'contact_groups': contactgroups,
        'escalation': escalations,
    }
    for relation in relations:
        if relation in host:
            ret_map = check_mapping(host[relation], relations[relation])
            if ret_map['all_found']:
                host[relation] = ret_map['data']
            else:
                to_update[relation] = host[relation]
                del host[relation]

    response = method_post(''.join([backend_url, 'host']), ujson.dumps(host), headers, auth)
    if '_error' in response and '_issues' in response:
        print "ERROR: %s" % response['_issues']
    else:
        hosts[host['host_name']] = response['_id']
        if to_update:
            to_update['_etag'] = response['_etag']
            host_update[response['_id']] = to_update

# Update use of host
print "~~~~~~~~~~~~~~~~~~~~ update 'use' in hosts ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
id_to_del = []
for id in host_update:
    if 'use' in host_update[id]:
        if host_update[id]['use'] in hosts:
            data = {'use': hosts[host_update[id]['use']]}
            headers['If-Match'] = host_update[id]['_etag']
            response = method_patch(''.join([backend_url, 'host', '/', id]),
                         ujson.dumps(data), headers, auth)
            host_update[id]['_etag'] = response['_etag']
            del host_update[id]['use']
        else:
            print 'ERROR: use host `%s` not found' % (host_update[id]['use'])
            del host_update[id]['use']
        if len(host_update[id]) == 1:
            id_to_del.append(id)
for id in id_to_del:
    del host_update[id]

# Update other lists of host
relations = {
    'parents': hosts,
    'hostgroups': hostgroups,
    'contacts': contacts,
    'contact_groups': contactgroups,
#    'escalation': escalations,
}
for relation in relations:
    print "~~~~~~~~~~~~~~~~~~~~ update '%s' in hosts ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" % (relation)
    id_to_del = []
    for id in host_update:
        if relation in host_update[id]:
            new_list = []
            for members in host_update[id][relation]:
                if members in hosts:
                    new_list.append(hosts[members])
                else:
                    print 'ERROR: %s host `%s` not found' % (relation, members)
            data = {relation: new_list}
            headers['If-Match'] = host_update[id]['_etag']
            response = method_patch(''.join([backend_url, 'host', '/', id]),
                         ujson.dumps(data), headers, auth)
            host_update[id]['_etag'] = response['_etag']
            del host_update[id][relation]
            if len(host_update[id]) == 1:
                id_to_del.append(id)
    for id in id_to_del:
        del host_update[id]

print "~~~~~~~~~~~~~~~~~~~~ update 'members' in hostgroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
id_to_del = []
for id in hostgroup_update:
    new_list = []
    for members in hostgroup_update[id]['members']:
        if members in host:
            new_list.append(hosts[members])
    data = {'members': new_list}
    headers['If-Match'] = hostgroup_update[id]['_etag']
    response = method_patch(''.join([backend_url, 'hostgroup', '/', id]),
                 ujson.dumps(data), headers, auth)
    hostgroup_update[id]['_etag'] = response['_etag']
    if len(hostgroup_update[id]) == 1:
        id_to_del.append(id)
for id in id_to_del:
    del hostgroup_update[id]

print "~~~~~~~~~~~~~~~~~~~~ Add servicegroups ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
headers = {'content-type': 'application/json'}
schema = servicegroup_get_schema()
# servicegroup to add later if required
servicegroup_update = {}
for servicegroup in conf['servicegroup']:
    to_update = {}
    servicegroup = update_types(servicegroup, schema['schema'])
    if 'members' in servicegroup:
        to_update['members'] = servicegroup['members']
        del servicegroup['members']
    if 'imported_from' in servicegroup:
        del servicegroup['imported_from']
    if 'servicegroup_members' in servicegroup:
        ret_map = check_mapping(servicegroup['servicegroup_members'], servicegroups)
        if ret_map['all_found']:
            servicegroup['servicegroup_members'] = ret_map['data']
        else:
            to_update['servicegroup_members'] = servicegroup['servicegroup_members']
            del servicegroup['servicegroup_members']
    response = method_post(''.join([backend_url, 'servicegroup']), ujson.dumps(servicegroup), headers, auth)
    servicegroups[servicegroup['servicegroup_name']] = response['_id']
    if to_update:
        to_update['_etag'] = response['_etag']
        servicegroup_update[response['_id']] = to_update

print "~~~~~~~~~~~~~~~~~~~~ update 'servicegroup_members' in servicegroups ~~~~~~~~~~~~~~~~~~~~"
id_to_del = []
for id in servicegroup_update:
    new_list = []
    for members in servicegroup_update[id]['servicegroup_members']:
        new_list.append(servicegroups[members])
    data = {'servicegroup_members': new_list}
    headers['If-Match'] = servicegroup_update[id]['_etag']
    response = method_patch(''.join([backend_url, 'servicegroup', '/', id]),
                 ujson.dumps(data), headers, auth)
    servicegroup_update[id]['_etag'] = response['_etag']
    if not 'members' in servicegroup_update[id]:
        id_to_del.append(id)
for id in id_to_del:
    del servicegroup_update[id]

print "~~~~~~~~~~~~~~~~~~~~ Add services ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

headers = {'content-type': 'application/json'}
schema = service_get_schema()
service_update = {}
for service in conf['service']:
    to_update = {}
    service = update_types(service, schema['schema'])
    if 'imported_from' in service:
        del service['imported_from']
    if 'use' in service:
        to_update['use'] = service['use']
        del service['use']
    if 'check_command' in service:
        if 'bp_rule' in service['check_command']:
            service['check_command_args'] = service['check_command']
            service['check_command'] = None
        elif '!' in service['check_command']:
            args = service['check_command'].split('!')
            service['check_command'] = args[0]
            del args[0]
            service['check_command_args'] = '!'.join(args)
            service['check_command'] = commands[service['check_command']]
        else:
            service['check_command'] = commands[service['check_command']]
    if 'host_name' in service:
        service['host_name'] = hosts[service['host_name']]
    if 'check_period' in service:
        service['check_period'] = timeperiods[service['check_period']]
    if 'notification_period' in service:
        service['notification_period'] = timeperiods[service['notification_period']]
    if 'maintenance_period' in service:
        service['maintenance_period'] = timeperiods[service['maintenance_period']]
    relations = {
        'servicegroups': servicegroups,
        'contacts': contacts,
        'contact_groups': contactgroups,
        'escalation': escalations,
        'service_dependencies': services,
    }
    for relation in relations:
        if relation in service:
            ret_map = check_mapping(service[relation], relations[relation])
            if ret_map['all_found']:
                service[relation] = ret_map['data']
            else:
                to_update[relation] = service[relation]
                del service[relation]
    response = method_post(''.join([backend_url, 'service']), ujson.dumps(service), headers, auth)
    if '_error' in response and '_issues' in response:
        print "ERROR: %s" % response['_issues']
    else:
        if 'service_description' in service:
            services[service['service_description']] = response['_id']
        else:
            services[service['name']] = response['_id']
        if to_update:
            to_update['_etag'] = response['_etag']
            service_update[response['_id']] = to_update

# Update use of service
print "~~~~~~~~~~~~~~~~~~~~ update 'use' in services ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
id_to_del = []
for id in service_update:
    if 'use' in service_update[id]:
        if service_update[id]['use'] in services:
            data = {'use': services[service_update[id]['use']]}
            headers['If-Match'] = service_update[id]['_etag']
            response = method_patch(''.join([backend_url, 'service', '/', id]),
                         ujson.dumps(data), headers, auth)
            service_update[id]['_etag'] = response['_etag']
            del service_update[id]['use']
        else:
            print 'ERROR: use service `%s` not found' % (service_update[id]['use'])
            del service_update[id]['use']
        if len(service_update[id]) == 1:
            id_to_del.append(id)
for id in id_to_del:
    del service_update[id]
