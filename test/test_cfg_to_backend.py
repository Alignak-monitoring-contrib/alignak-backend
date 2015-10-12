#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2
import requests
import time
import subprocess
import json
from alignak_backend_client.client import Backend


class TestCfgToBackend(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
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

    def test_command_with_template(self):

        q = subprocess.Popen(['../tools/cfg_to_backend.py', 'alignak_cfg_files/commands.cfg'])
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

        ref = {"use": template_id, "name": "", "command_name": "check_tcp",
               "definition_order": 100, "register": True,
               "command_line": "$PLUGINSDIR$/check_tcp  -H $HOSTADDRESS$ -p $ARG1$",
               "poller_tag": "None", "reactionner_tag": "None", "module_type": "fork",
               "timeout": -1, "enable_environment_macros": False}
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
        # for comm in r['_items']:
        #     if 'name' in comm and comm['name'] == 'template01':
        #         template_id = comm['_id']
        #         ref = {"name": "template01", "definition_order": 50, "register": False,
        #                "poller_tag": "None", "reactionner_tag": "None", "module_type": "fork",
        #                "timeout": 15, "enable_environment_macros": False}
        #         del comm['_links']
        #         del comm['_id']
        #         del comm['_etag']
        #         del comm['_created']
        #         del comm['_updated']
        #         self.assertEqual(comm, ref)
        #     else:
        #         reg_comm = comm.copy()
        #
        # ref = {"use": template_id, "name": "", "command_name": "check_tcp",
        #        "definition_order": 100, "register": True,
        #        "command_line": "$PLUGINSDIR$/check_tcp  -H $HOSTADDRESS$ -p $ARG1$",
        #        "poller_tag": "None", "reactionner_tag": "None", "module_type": "fork",
        #        "timeout": -1, "enable_environment_macros": False}
        # del reg_comm['_links']
        # del reg_comm['_id']
        # del reg_comm['_etag']
        # del reg_comm['_created']
        # del reg_comm['_updated']
        # print(ref)
        # print(reg_comm)
        # self.assertEqual(reg_comm, ref)

