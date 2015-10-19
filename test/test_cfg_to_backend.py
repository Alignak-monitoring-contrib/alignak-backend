#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2
import time
import subprocess
from alignak_backend_client.client import Backend


class TestCfgToBackend(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff=None
        cls.p = subprocess.Popen(['uwsgi', '-w', 'alignakbackend:app', '--socket', '0.0.0.0:5000', '--protocol=http', '--enable-threads'])
        time.sleep(3)
        cls.backend = Backend('http://127.0.0.1:5000')
        cls.backend.login("admin", "admin", "force")
        cls.backend.delete("host", {})
        cls.backend.delete("service", {})
        cls.backend.delete("command", {})
        cls.backend.delete("livestate", {})
        cls.backend.delete("livesynthesis", {})

    @classmethod
    def tearDownClass(cls):
        cls.backend.delete("contact", {})
        cls.p.kill()

    @classmethod
    def tearDown(cls):
        cls.backend.delete("command", {})
        cls.backend.delete("timeperiod", {})

    def test_command_with_double_template(self):

        q = subprocess.Popen(['../tools/cfg_to_backend.py', 'alignak_cfg_files/commands.cfg'])
        q.communicate() #now wait

        r = self.backend.get('command')
        self.assertEqual(len(r['_items']), 3)
        templates_id = {}
        for comm in r['_items']:
            if 'name' in comm and comm['name'] == 'template01':
                templates_id['template01'] = comm['_id']
                ref = {"name": "template01", "definition_order": 50, "register": False,
                       "poller_tag": "None", "reactionner_tag": "None", "module_type": "fork",
                       "timeout": 15, "enable_environment_macros": False}
                del comm['_links']
                del comm['_id']
                del comm['_etag']
                del comm['_created']
                del comm['_updated']
                self.assertEqual(comm, ref)
            elif 'name' in comm and comm['name'] == 'template02':
                templates_id['template02'] = comm['_id']
                ref = {u"name": u"template02", u"definition_order": 100, u"register": False,
                       u"poller_tag": u"None", u"reactionner_tag": u"None", u"module_type": u"fork",
                       u"timeout": 17, u"enable_environment_macros": False}
                del comm['_links']
                del comm['_id']
                del comm['_etag']
                del comm['_created']
                del comm['_updated']
                print(ref)
                print(comm)
                self.assertEqual(comm, ref)

            else:
                reg_comm = comm.copy()

        use_templates = [templates_id['template01'], templates_id['template02']]
        ref = {u"use": use_templates, u"name": u"", u"command_name": u"check_tcp",
               u"definition_order": 50, u"register": True,
               u"command_line": u"$PLUGINSDIR$/check_tcp  -H $HOSTADDRESS$ -p $ARG1$",
               u"poller_tag": u"None", u"reactionner_tag": u"None", u"module_type": u"fork",
               u"timeout": 15, u"enable_environment_macros": False}
        del reg_comm['_links']
        del reg_comm['_id']
        del reg_comm['_etag']
        del reg_comm['_created']
        del reg_comm['_updated']
        self.assertEqual(reg_comm, ref)

    def test_command_with_template(self):

        q = subprocess.Popen(['../tools/cfg_to_backend.py', 'alignak_cfg_files/commands2.cfg'])
        q.communicate() #now wait

        r = self.backend.get('command')
        self.assertEqual(len(r['_items']), 2)
        for comm in r['_items']:
            if 'name' in comm and comm['name'] == 'template01':
                template_id = comm['_id']
                ref = {"name": "template01", "definition_order": 50, "register": False,
                       "poller_tag": "None", "reactionner_tag": "None", "module_type": "fork",
                       "timeout": 15, "enable_environment_macros": False}
                del comm['_links']
                del comm['_id']
                del comm['_etag']
                del comm['_created']
                del comm['_updated']
                self.assertEqual(comm, ref)
            else:
                reg_comm = comm.copy()

        ref = {"use": [template_id], "name": "", "command_name": "check_tcp",
               "definition_order": 50, "register": True,
               "command_line": "$PLUGINSDIR$/check_tcp  -H $HOSTADDRESS$ -p $ARG1$",
               "poller_tag": "None", "reactionner_tag": "None", "module_type": "fork",
               "timeout": 15, "enable_environment_macros": False}
        del reg_comm['_links']
        del reg_comm['_id']
        del reg_comm['_etag']
        del reg_comm['_created']
        del reg_comm['_updated']
        self.assertEqual(reg_comm, ref)

    def test_timeperiod(self):

        q = subprocess.Popen(['../tools/cfg_to_backend.py', 'alignak_cfg_files/timeperiods.cfg'])
        q.communicate() #now wait

        r = self.backend.get('timeperiod')
        self.assertEqual(len(r['_items']), 1)
        for comm in r['_items']:
             ref = {u"name": u"", u"timeperiod_name": u"workhours",
                    u"definition_order": 100, u"register": True,
                    u"alias": u"Normal Work Hours",
                    u"dateranges": [{u'monday': u'09:00-17:00'}, {u'tuesday': u'09:00-17:00'},
                                   {u'friday': u'09:00-17:00'}, {u'wednesday': u'09:00-17:00'},
                                   {u'thursday': u'09:00-17:00'}],
                    u"exclude": [], u"is_active": False, u"imported_from": u""}
             del comm['_links']
             del comm['_id']
             del comm['_etag']
             del comm['_created']
             del comm['_updated']
             self.assertEqual(comm, ref)

    def test_host_multiple_link_later(self):
        q = subprocess.Popen(['../tools/cfg_to_backend.py', 'alignak_cfg_files/hosts_links_parent.cfg'])
        q.communicate() #now wait

        r = self.backend.get('host')
        self.assertEqual(len(r['_items']), 4)
        hosts = {}
        for comm in r['_items']:
            if 'host_name' in comm and comm['host_name'] == 'webui':
                webui_host = comm.copy()
            elif 'host_name' in comm:
                hosts[comm['host_name']] = comm['_id']
            else:
                template_id = comm['_id']

        parents = []
        parents.append(hosts['backend'])
        parents.append(hosts['mongo'])

        ref = {u"name": u"", u"host_name": u"webui",
               u"parents": parents, u'statusmap_image': u'', u'business_impact_modulations': [],
               u'flap_detection_options': [u'o', u'd', u'u'], u'labels': [], u'action_url': u'',
               u'escalations': [], u'low_flap_threshold': 25, u'process_perf_data': True,
               u'business_rule_downtime_as_ack': False, u'snapshot_interval': 5,
               u'display_name': u"Fred's testing server", u'notification_interval': 1440,
               u'failure_prediction_enabled': False, u'retry_interval': 0,
               u'snapshot_enabled': False, u'event_handler_enabled': False, u'trigger': u'',
               u'initial_state': u'u', u'first_notification_delay': 0,
               u'notification_options': [u'd', u'u', u'r', u'f'],
               u'snapshot_period': u'', u'notifications_enabled': True, u'event_handler': u'',
               u'snapshot_command': u'', u'freshness_threshold': 0, u'check_command_args': u'',
               u'service_excludes': [], u'imported_from': u'', u'time_to_orphanage': 300,
               u'trigger_broker_raise_enabled': False, u'name': u'', u'custom_views': [],
               u'ui': True, u'passive_checks_enabled': True, u'check_interval': 5, u'notes': u'',
               u'check_freshness': False, u'active_checks_enabled': True, u'icon_image_alt': u'',
               u'service_includes': [], u'reactionner_tag': u'None', u'notes_url': u'',
               u'service_overrides': [], u'maintenance_period': u'', u'realm': u'All',
               u'poller_tag': u'None', u'trending_policies': [], u'resultmodulations': [],
               u'retain_status_information': True, u'icon_image': u'', u'stalking_options': [],
               u'snapshot_criteria': [u'd', u'u'], u'flap_detection_enabled': True,
               u'business_rule_host_notification_options': [u'd', u'u', u'r', u'f', u's'],
               u'high_flap_threshold': 50, u'definition_order': 100, u'macromodulations': [],
               u'retain_nonstatus_information': True, u'business_rule_smart_notifications': False,
               u'vrml_image': u'', u'address': u'192.160.20.1', u'trigger_name': u'',
               u'3d_coords': u'', u'2d_coords': u'', u'register': True, u'checkmodulations': [],
               u'alias': u'Alignak on FreeBSD', u'icon_set': u'', u'business_impact': 4,
               u'max_check_attempts': 2, u'business_rule_output_template': u'',
               u'business_rule_service_notification_options': [u'w', u'u', u'c', u'r', u'f', u's'],
               u"use": [template_id], u'obsess_over_host': False,}
        del webui_host['_links']
        del webui_host['_id']
        del webui_host['_etag']
        del webui_host['_created']
        del webui_host['_updated']
        self.assertEqual(webui_host, ref)

    def test_host_multiple_link_now(self):
        #host.hostgroups
        q = subprocess.Popen(['../tools/cfg_to_backend.py', 'alignak_cfg_files/hosts_links_hostgroup.cfg'])
        q.communicate() #now wait

        r = self.backend.get('host')
        self.assertEqual(len(r['_items']), 2)
        hosts = {}
        for comm in r['_items']:
            if 'host_name' in comm and comm['host_name'] == 'webui':
                webui_host = comm.copy()
            else:
                template_id = comm['_id']
        hostgroups = []
        rhg = self.backend.get('hostgroup')
        for comm in rhg['_items']:
            hostgroups.append(comm['_id'])

        ref = {u"name": u"", u"host_name": u"webui",
               u"hostgroups": hostgroups, u'statusmap_image': u'', u'business_impact_modulations': [],
               u'flap_detection_options': [u'o', u'd', u'u'], u'labels': [], u'action_url': u'',
               u'escalations': [], u'low_flap_threshold': 25, u'process_perf_data': True,
               u'business_rule_downtime_as_ack': False, u'snapshot_interval': 5,
               u'display_name': u"Fred's testing server", u'notification_interval': 1440,
               u'failure_prediction_enabled': False, u'retry_interval': 0,
               u'snapshot_enabled': False, u'event_handler_enabled': False, u'trigger': u'',
               u'initial_state': u'u', u'first_notification_delay': 0,
               u'notification_options': [u'd', u'u', u'r', u'f'],
               u'snapshot_period': u'', u'notifications_enabled': True, u'event_handler': u'',
               u'snapshot_command': u'', u'freshness_threshold': 0, u'check_command_args': u'',
               u'service_excludes': [], u'imported_from': u'', u'time_to_orphanage': 300,
               u'trigger_broker_raise_enabled': False, u'name': u'', u'custom_views': [],
               u'ui': True, u'passive_checks_enabled': True, u'check_interval': 5, u'notes': u'',
               u'check_freshness': False, u'active_checks_enabled': True, u'icon_image_alt': u'',
               u'service_includes': [], u'reactionner_tag': u'None', u'notes_url': u'',
               u'service_overrides': [], u'maintenance_period': u'', u'realm': u'All',
               u'poller_tag': u'None', u'trending_policies': [], u'resultmodulations': [],
               u'retain_status_information': True, u'icon_image': u'', u'stalking_options': [],
               u'snapshot_criteria': [u'd', u'u'], u'flap_detection_enabled': True,
               u'business_rule_host_notification_options': [u'd', u'u', u'r', u'f', u's'],
               u'high_flap_threshold': 50, u'definition_order': 100, u'macromodulations': [],
               u'retain_nonstatus_information': True, u'business_rule_smart_notifications': False,
               u'vrml_image': u'', u'address': u'192.160.20.1', u'trigger_name': u'',
               u'3d_coords': u'', u'2d_coords': u'', u'register': True, u'checkmodulations': [],
               u'alias': u'Alignak on FreeBSD', u'icon_set': u'', u'business_impact': 4,
               u'max_check_attempts': 2, u'business_rule_output_template': u'',
               u'business_rule_service_notification_options': [u'w', u'u', u'c', u'r', u'f', u's'],
               u"use": [template_id], u'obsess_over_host': False,}
        del webui_host['_links']
        del webui_host['_id']
        del webui_host['_etag']
        del webui_host['_created']
        del webui_host['_updated']
        self.assertEqual(webui_host, ref)
