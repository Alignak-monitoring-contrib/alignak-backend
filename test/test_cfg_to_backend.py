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
        cls.backend.delete("timeperiod", {})
        cls.backend.delete("livestate", {})
        cls.backend.delete("livesynthesis", {})

    @classmethod
    def tearDownClass(cls):
        cls.backend.delete("contact", {})
        cls.p.kill()

    @classmethod
    def tearDown(cls):
        cls.backend.delete("host", {})
        cls.backend.delete("service", {})
        cls.backend.delete("command", {})
        cls.backend.delete("timeperiod", {})
        cls.backend.delete("livestate", {})
        cls.backend.delete("livesynthesis", {})

    def test_host_with_double_template(self):

        q = subprocess.Popen(['../alignak_backend/tools/cfg_to_backend.py', '--delete', 'alignak_cfg_files/hosts.cfg'])
        (stdoutdata, stderrdata) = q.communicate() # now wait

        r = self.backend.get('host')
        self.assertEqual(len(r['_items']), 1)
        for comm in r['_items']:
            reg_comm = comm.copy()

        self.assertEqual(reg_comm['name'], 'srv01')
        self.assertEqual(reg_comm['max_check_attempts'], 6)
        self.assertEqual(reg_comm['check_interval'], 2)

    def test_host_with_template(self):

        q = subprocess.Popen(['../alignak_backend/tools/cfg_to_backend.py', '--delete', 'alignak_cfg_files/hosts2.cfg'])
        (stdoutdata, stderrdata) = q.communicate() # now wait

        r = self.backend.get('host')
        self.assertEqual(len(r['_items']), 1)
        for comm in r['_items']:
            reg_comm = comm.copy()

        self.assertEqual(reg_comm['name'], 'srv01')
        self.assertEqual(reg_comm['address'], '192.168.1.10')
        self.assertEqual(reg_comm['check_interval'], 4)
        self.assertEqual(reg_comm['max_check_attempts'], 6)

    def test_timeperiod(self):
        q = subprocess.Popen(['../alignak_backend/tools/cfg_to_backend.py', '--delete', 'alignak_cfg_files/timeperiods.cfg'])
        (stdoutdata, stderrdata) = q.communicate() # now wait

        r = self.backend.get('timeperiod')
        self.assertEqual(len(r['_items']), 1)
        for comm in r['_items']:
             ref = {u"name": u"workhours",
                    u"definition_order": 100,
                    u"alias": u"Normal Work Hours",
                    u"dateranges": [{u'monday': u'09:00-17:00'}, {u'tuesday': u'09:00-17:00'},
                                   {u'friday': u'09:00-12:00,14:00-16:00'}, {u'wednesday': u'09:00-17:00'},
                                   {u'thursday': u'09:00-17:00'}],
                    u"exclude": [], u"is_active": False, u"imported_from": u""}
             del comm['_links']
             del comm['_id']
             del comm['_etag']
             del comm['_created']
             del comm['_updated']
             del comm['_realm']
             self.assertEqual(comm, ref)

    def test_timeperiod_complex(self):
        q = subprocess.Popen(['../alignak_backend/tools/cfg_to_backend.py', '--delete', 'alignak_cfg_files/timeperiods_complex.cfg'])
        (_, _) = q.communicate() # now wait

        r = self.backend.get_all('timeperiod')
        self.assertEqual(len(r), 2)
        ref = {u"name": u"workhours",
               u"definition_order": 100,
               u"alias": u"Normal Work Hours",
               u"dateranges": [{u'monday': u'09:00-17:00'}, {u'tuesday': u'09:00-17:00'},
                               {u'friday': u'09:00-12:00,14:00-16:00'}, {u'wednesday': u'09:00-17:00'},
                               {u'thursday': u'09:00-17:00'}],
               u"exclude": [u'us-holidays'], u"is_active": False, u"imported_from": u""}
        comm = r[0]
        del comm['_links']
        del comm['_id']
        del comm['_etag']
        del comm['_created']
        del comm['_updated']
        del comm['_realm']
        self.assertItemsEqual(comm, ref)

        ref = {u"name": u"us-holidays",
               u"definition_order": 100,
               u"alias": u"U.S. Holidays",
               u"dateranges": [{u'thursday -1 november': u'00:00-00:00'},
                               {u'monday 1 september': u'00:00-00:00'},
                               {u'january 1': u'00:00-00:00'},
                               {u'december 25': u'00:00-00:00'}, {u'july 4': u'00:00-00:00'}],
               u"exclude": [], u"is_active": False, u"imported_from": u""}
        comm = r[1]
        del comm['_links']
        del comm['_id']
        del comm['_etag']
        del comm['_created']
        del comm['_updated']
        del comm['_realm']
        self.assertItemsEqual(comm, ref)

    def test_host_multiple_link_later(self):
        q = subprocess.Popen(['../alignak_backend/tools/cfg_to_backend.py', '--delete', 'alignak_cfg_files/hosts_links_parent.cfg'])
        (stdoutdata, stderrdata) = q.communicate() # now wait

        t = self.backend.get('timeperiod')
        for timep in t['_items']:
            timeperiod = timep['_id']

        r = self.backend.get('host')
        self.assertEqual(len(r['_items']), 3)
        hosts = {}
        for comm in r['_items']:
            if comm['name'] == 'webui':
                webui_host = comm.copy()
            else:
                hosts[comm['name']] = comm['_id']

        parents = []
        parents.append(hosts['backend'])
        parents.append(hosts['mongo'])
        self.assertEqual(webui_host['name'], 'webui')
        self.assertEqual(webui_host['parents'], parents)

    def test_host_multiple_link_now(self):
        """
        The host will be added in host_group endpoint

        :return: None
        """
        # host.hostgroups
        q = subprocess.Popen(['../alignak_backend/tools/cfg_to_backend.py', '--delete', 'alignak_cfg_files/hosts_links_hostgroup.cfg'])
        (stdoutdata, stderrdata) = q.communicate() # now wait

        r = self.backend.get('host')
        self.assertEqual(len(r['_items']), 1)
        for comm in r['_items']:
            host_id = comm['_id']
        hostgroups = []
        rhg = self.backend.get('hostgroup')
        for comm in rhg['_items']:
            self.assertEqual(comm['members'], [host_id])

    def test_command_with_args(self):

        q = subprocess.Popen(['../alignak_backend/tools/cfg_to_backend.py', '--delete', 'alignak_cfg_files/hosts.cfg'])
        (stdoutdata, stderrdata) = q.communicate() # now wait

        c = self.backend.get('command')
        self.assertEqual(len(c['_items']), 1)
        command_id = ''
        for co in c['_items']:
            command_id = co['_id']

        r = self.backend.get('host')
        self.assertEqual(len(r['_items']), 1)
        for comm in r['_items']:
            reg_comm = comm.copy()

        self.assertEqual(reg_comm['name'], 'srv01')
        self.assertEqual(reg_comm['check_command_args'], '3306!5!8')
        self.assertEqual(reg_comm['check_command'], command_id)

        co = self.backend.get_all('command')
        self.assertEqual(len(co), 1)
        self.assertEqual(co[0]['name'], "check_tcp")

    def test_contact_is_admin(self):
        q = subprocess.Popen(['../alignak_backend/tools/cfg_to_backend.py', '--delete', 'alignak_cfg_files/contact_admin.cfg'])
        (stdoutdata, stderrdata) = q.communicate() # now wait

        co = self.backend.get_all('contact')
        self.assertEqual(len(co), 2)

        self.assertEqual(co[1]['is_admin'], True)
        self.assertEqual(co[1]['back_role_super_admin'], True)

    def test_host_customvariables(self):
        q = subprocess.Popen(['../alignak_backend/tools/cfg_to_backend.py', '--delete', 'alignak_cfg_files/hosts_custom_variables.cfg'])
        (stdoutdata, stderrdata) = q.communicate() # now wait

        ho = self.backend.get_all('host')
        self.assertEqual(len(ho), 1)
        self.assertEqual(ho[0]['_GPS_LOC'], '45')

