#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.template`` module

    This module manages the templates (host / services)
"""
from __future__ import print_function
from flask import current_app, g, request, abort
from eve.methods.post import post_internal
from eve.methods.patch import patch_internal
from eve.render import send_response
from bson.objectid import ObjectId
from alignak_backend.models.host import get_schema as host_schema
from alignak_backend.models.service import get_schema as service_schema


class Template(object):
    """
        Template class
    """

    @staticmethod
    def pre_post_host(user_request):
        """
        If we use templates, we fill fields with template values

        :param user_request: request of the user
        :type user_request: object
        :return: None
        """
        if isinstance(user_request.json, dict):
            Template.fill_template_host(user_request.json)
        else:
            for i in user_request.json:
                Template.fill_template_host(i)

    @staticmethod
    def fill_template_host(item):
        """
        Prepare fields of host with fields of host templates

        :param item: field name / values of the host
        :type item: dict
        :return: None
        """
        host = current_app.data.driver.db['host']
        ignore_fields = ['_id', '_etag', '_updated', '_created', '_template_fields', '_templates',
                         '_is_template', 'realm']
        fields_not_update = []
        for field_name, field_value in item.iteritems():
            fields_not_update.append(field_name)
        item['_template_fields'] = []
        if ('_is_template' not in item or not item['_is_template']) \
                and '_templates' in item and item['_templates'] != []:
            for host_template in item['_templates']:
                hosts = host.find_one({'_id': ObjectId(host_template)})
                if hosts is not None:
                    for field_name, field_value in hosts.iteritems():
                        if field_name not in fields_not_update \
                                and field_name not in ignore_fields:
                            item[field_name] = field_value
                            item['_template_fields'].append(field_name)
            schema = host_schema()
            ignore_schema_fields = ['realm', '_template_fields', '_templates', '_is_template']
            for key in schema['schema'].iterkeys():
                if key not in ignore_schema_fields:
                    if key not in item:
                        item['_template_fields'].append(key)

    @staticmethod
    def on_update_host(updates, original):
        """
        On update host, if not template, remove in '_template_fields' fields in updates because
        we update these fields, so they are now not dependant of template

        :param updates: modified fields
        :type updates: dict
        :param original: original fields
        :type original: dict
        :return: None
        """
        if g.get('ignore_hook_patch', False):
            return
        if not original['_is_template']:
            ignore_schema_fields = ['realm', '_template_fields', '_templates', '_is_template']
            for field_name, field_value in updates.iteritems():
                if field_name not in ignore_schema_fields:
                    if field_name in original['_template_fields']:
                        original['_template_fields'].remove(field_name)
            updates['_template_fields'] = original['_template_fields']

    @staticmethod
    def on_updated_host(updates, original):
        """
        After host updated, if host is a template, report value of fields updated on host used
        this template

        :param updates: modified fields
        :type updates: dict
        :param original: original fields
        :type original: dict
        :return: None
        """
        if g.get('ignore_hook_patch', False):
            g.ignore_hook_patch = False
            return
        if original['_is_template']:
            # We must update all host use this template
            host_db = current_app.data.driver.db['host']
            hosts = host_db.find({'_templates': original['_id']})
            for host in hosts:
                Template.update_host_use_template(host, updates)

    @staticmethod
    def update_host_use_template(host, fields):
        """
        This update (patch) host with values of template

        :param host: fields / values of the host
        :type host: dict
        :param fields: fields updated in the template host
        :type fields: dict
        :return: None
        """
        host_db = current_app.data.driver.db['host']
        template_fields = {}
        for template_id in host['_templates']:
            temp = host_db.find_one({'_id': template_id})
            for name, value in temp.iteritems():
                template_fields[name] = value
        to_patch = {}
        for name, value in fields.iteritems():
            if name in host['_template_fields']:
                to_patch[name] = template_fields[name]
        if len(to_patch) > 0:
            g.ignore_hook_patch = True
            lookup = {"_id": host['_id']}
            patch_internal('host', to_patch, False, False, **lookup)

    @staticmethod
    def pre_post_service(user_request):
        """
        If we use templates, we fill fields with template values

        :param user_request: request of the user
        :type user_request: object
        :return: None
        """
        if isinstance(user_request.json, dict):
            Template.fill_template_service(user_request.json)
        else:
            for i in user_request.json:
                Template.fill_template_service(i)

    @staticmethod
    def fill_template_service(item):
        """
        Prepare fields of service with fields of service templates

        :param item: field name / values of the service
        :type item: dict
        :return: None
        """
        service = current_app.data.driver.db['service']
        ignore_fields = ['_id', '_etag', '_updated', '_created', '_template_fields', '_templates',
                         '_is_template', '_realm', 'host_name']
        fields_not_update = []
        for field_name, field_value in item.iteritems():
            fields_not_update.append(field_name)
        item['_template_fields'] = []
        if ('_is_template' not in item or not item['_is_template']) \
                and '_templates' in item and item['_templates'] != []:
            for service_template in item['_templates']:
                services = service.find_one({'_id': ObjectId(service_template)})
                if services is not None:
                    for field_name, field_value in services.iteritems():
                        if field_name not in fields_not_update \
                                and field_name not in ignore_fields:
                            item[field_name] = field_value
                            item['_template_fields'].append(field_name)
            schema = service_schema()
            ignore_schema_fields = ['_realm', '_template_fields', '_templates', '_is_template']
            for key in schema['schema'].iterkeys():
                if key not in ignore_schema_fields:
                    if key not in item:
                        item['_template_fields'].append(key)

    @staticmethod
    def on_update_service(updates, original):
        """
        On update service, if not template, remove in '_template_fields' fields in updates because
        we update these fields, so they are now not dependant of template

        :param updates: modified fields
        :type updates: dict
        :param original: original fields
        :type original: dict
        :return: None
        """
        if g.get('ignore_hook_patch', False):
            return
        if not original['_is_template']:
            ignore_schema_fields = ['realm', '_template_fields', '_templates', '_is_template']
            for field_name, field_value in updates.iteritems():
                if field_name not in ignore_schema_fields:
                    if field_name in original['_template_fields']:
                        original['_template_fields'].remove(field_name)
            updates['_template_fields'] = original['_template_fields']

    @staticmethod
    def on_updated_service(updates, original):
        """
        After service updated, if service is a template, report value of fields updated on
        service used this template

        :param updates: modified fields
        :type updates: dict
        :param original: original fields
        :type original: dict
        :return: None
        """
        if g.get('ignore_hook_patch', False):
            g.ignore_hook_patch = False
            return
        if original['_is_template']:
            # We must update all service use this template
            service_db = current_app.data.driver.db['service']
            services = service_db.find({'_templates': original['_id']})
            for service in services:
                Template.update_service_use_template(service, updates)

    @staticmethod
    def update_service_use_template(service, fields):
        """
        This update (patch) service with values of template

        :param service: fields / values of the service
        :type service: dict
        :param fields: fields updated in the template service
        :type fields: dict
        :return: None
        """
        service_db = current_app.data.driver.db['service']
        template_fields = {}
        for template_id in service['_templates']:
            temp = service_db.find_one({'_id': template_id})
            for name, value in temp.iteritems():
                template_fields[name] = value
        to_patch = {}
        for name, value in fields.iteritems():
            if name in service['_template_fields']:
                to_patch[name] = template_fields[name]
        if len(to_patch) > 0:
            g.ignore_hook_patch = True
            lookup = {"_id": service['_id']}
            patch_internal('service', to_patch, False, False, **lookup)
