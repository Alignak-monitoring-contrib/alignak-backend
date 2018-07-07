#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check is backend is running without error
"""

from __future__ import print_function

import os
import time
import json
import shlex
import subprocess
import requests
import unittest2
import pytest


class TestStart(unittest2.TestCase):
    """Test the different application start mode"""
    def _some_activity(self):
        # pylint: disable=attribute-defined-outside-init
        """ Some activity on the backend API"""
        headers = {'Content-Type': 'application/json'}
        params = {'username': 'admin', 'password': 'admin'}

        # Log onto the backend
        response = requests.post('http://127.0.0.1:5000/login', json=params, headers=headers)
        resp = response.json()
        assert resp['token']
        auth = requests.auth.HTTPBasicAuth(resp['token'], '')

        # Get default realm
        response = requests.get('http://127.0.0.1:5000/realm', auth=auth)
        resp = response.json()
        realm_all = resp['_items'][0]['_id']

        # Get admin user
        requests.get('http://127.0.0.1:5000/user', {"name": "admin"}, auth=auth)

        # Add a command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = realm_all
        requests.post('http://127.0.0.1:5000/command', json=data, headers=headers, auth=auth)
        response = requests.get('http://127.0.0.1:5000/command', auth=auth)
        resp = response.json()
        rc = resp['_items']

        # Add an host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = realm_all
        data['ls_last_check'] = 1234567890  # Fixed timestamp for test
        data['ls_state'] = 'UP'
        data['ls_state_type'] = 'HARD'
        data['ls_state_id'] = 0
        data['ls_perf_data'] = "rta=14.581000ms;1000.000000;3000.000000;0.000000 pl=0%;100;100;0"
        response = requests.post('http://127.0.0.1:5000/host', json=data,
                                 headers=headers, auth=auth)
        resp = response.json()
        response = requests.get('http://127.0.0.1:5000/host/' + resp['_id'], auth=auth)
        host_srv001 = response.json()

        # Add a service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = host_srv001['_id']
        data['check_command'] = rc[0]['_id']
        data['_realm'] = realm_all
        data['name'] = 'load'
        data['ls_last_check'] = 1234567890  # Fixed timestamp for test
        data['ls_state'] = 'OK'
        data['ls_state_type'] = 'HARD'
        data['ls_state_id'] = 0
        data['ls_perf_data'] = "load1=0.360;15.000;30.000;0; load5=0.420;10.000;25.000;0; " \
                               "load15=0.340;5.000;20.000;0;"
        requests.post('http://127.0.0.1:5000/service', json=data, headers=headers, auth=auth)

    def _backend_clean(self):
        """ Some activity on the backend API"""
        headers = {'Content-Type': 'application/json'}
        params = {'username': 'admin', 'password': 'admin'}

        # Log onto the backend
        response = requests.post('http://127.0.0.1:5000/login', json=params, headers=headers)
        resp = response.json()
        assert resp['token']
        auth = requests.auth.HTTPBasicAuth(resp['token'], '')

        for resource in ['host', 'service', 'command', 'history']:
            requests.delete('http://127.0.0.1:5000/' + resource, auth=auth)

    @classmethod
    def setUpClass(cls):
        """
        This method:
          * delete mongodb database
          * start the backend with uwsgi
          * log in the backend and get the token
          * get the realm

        :return: None
        """
        # Set test mode for Alignak backend
        os.environ['ALIGNAK_BACKEND_TEST'] = '1'
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-backend-test'
        os.environ['ALIGNAK_BACKEND_CONFIGURATION_FILE'] = './cfg/settings/settings.json'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split(
                'mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0

    def test_start_application_uwsgi(self):
        """ Start alignak backend with uwsgi"""

        os.getcwd()
        print("Launching application with UWSGI ...")

        test_dir = os.path.dirname(os.path.realpath(__file__))
        print("Dir: %s" % test_dir)

        print("Starting Alignak Backend...")
        subprocess.Popen(
            shlex.split('uwsgi --plugin python -w alignak_backend.app:app --socket 0.0.0.0:5000 '
                        '--protocol=http --enable-threads --pidfile /tmp/uwsgi.pid')
        )
        time.sleep(1)

        headers = {'Content-Type': 'application/json'}
        params = {'username': 'admin', 'password': 'admin'}

        # Log onto the backend
        response = requests.post('http://127.0.0.1:5000/login', json=params, headers=headers)
        resp = response.json()
        assert resp['token']

        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(2)

    def test_start_application_old(self):
        """ Start application old mode"""
        print('Start application old mode')

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(os.path.join(dir_path, "../alignak_backend"))
        print("Launching application default...")
        exit_code = subprocess.call(
            shlex.split('python ../alignak_backend/app.py')
        )
        assert exit_code == 1

        # Restore initial path
        os.chdir(dir_path)

    def test_start_application(self):
        """ Start application stand alone - default JSON (commented) configuration file"""
        os.environ['ALIGNAK_BACKEND_CONFIGURATION_FILE'] = \
            '../test/cfg/settings/settings.json'
        self._start_and_stop_app()

    def test_start_application_json_uncommented(self):
        """ Start application stand alone - uncommented JSON configuration file"""
        os.environ['ALIGNAK_BACKEND_CONFIGURATION_FILE'] = \
            '../test/cfg/settings/settings_uncommented.json'
        self._start_and_stop_app()
        os.environ['ALIGNAK_BACKEND_CONFIGURATION_FILE'] = \
            '../test/cfg/settings/settings.json'

    def test_start_application_json_escaped(self):
        """ Start application stand alone - escaped JSON configuration file
        Text fields containing / character are escaped as with a backslahs
        """
        os.environ['ALIGNAK_BACKEND_CONFIGURATION_FILE'] = \
            '../test/cfg/settings/settings_escaped_slashes.json'
        self._start_and_stop_app()
        os.environ['ALIGNAK_BACKEND_CONFIGURATION_FILE'] = \
            '../test/cfg/settings/settings.json'

    def test_start_application_json_unescaped(self):
        """ Start application stand alone - unescaped JSON configuration file
        Text fields containing / character need to be escaped with a backslahs
        """
        os.environ['ALIGNAK_BACKEND_CONFIGURATION_FILE'] = \
            '../test/cfg/settings/settings_unescaped.json'
        self._start_and_stop_app()
        os.environ['ALIGNAK_BACKEND_CONFIGURATION_FILE'] = \
            '../test/cfg/settings/settings.json'

    def _start_and_stop_app(self):
        if os.path.exists('/tmp/alignak-backend_alignak-backend.log'):
            os.remove('/tmp/alignak-backend_alignak-backend.log')

        print("Launching backend...")
        process = subprocess.Popen(
            shlex.split('python ../alignak_backend/main.py'),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print('PID = ', process.pid)
        time.sleep(1)

        ret = process.poll()
        if ret is not None:
            for line in iter(process.stdout.readline, b''):
                print("... " + line.rstrip())
            for line in iter(process.stderr.readline, b''):
                print("xxx " + line.rstrip())

        time.sleep(3)
        self._backend_clean()
        self._some_activity()
        time.sleep(3)

        print("Killing backend...")
        process.terminate()
        p_stdout = []
        found = False
        # todo: do not run correctly on Travis - no stdout/stderr fetched from the launched process!
        travis_run = 'TRAVIS' in os.environ
        for line in iter(process.stdout.readline, b''):
            p_stdout.append(str(line).rstrip())
            print(">>> " + str(line).rstrip())
            if b'Application settings:' in line:
                # Not escaped URL!
                if b"http://127.0.0.1:7770" in line:
                    found = True
        assert travis_run or found

        login = False
        p_stderr = []
        for line in iter(process.stderr.readline, b''):
            p_stderr.append(str(line).rstrip())
            print("*** " + str(line).rstrip())
            line = str(line)
            if 'POST /login HTTP/1.1' in line:
                login = True
        assert travis_run or found

        # Do not run correctly on Travis
        # todo: reactivate when problem is found !
        # print("Backend log file content:")
        # log_dirs = ['/usr/local/var/log/alignak-backend', '/var/log/alignak-backend',
        #             '/usr/local/var/log/alignak', '/var/log/alignak',
        #             '/usr/local/var/log', '/var/log']
        # for log_dir in log_dirs:
        #     # Directory exists and is writable
        #     if os.path.isdir(log_dir) and os.access(log_dir, os.W_OK):
        #         print("Backend log directory: %s" % (log_dir))
        #         if os.path.exists('%s/alignak-backend_alignak-backend.log' % log_dir):
        #             break
        # else:
        #     log_dir = '/tmp'
        #
        # with open('%s/alignak-backend_alignak-backend.log' % log_dir) as f:
        #     for line in f:
        #         print(line[:-1])

        return p_stdout, p_stderr

    def test_start_application_old_settings(self):
        """ Start application stand alone - old settings file (no logger)"""
        os.environ['ALIGNAK_BACKEND_CONFIGURATION_FILE'] = \
            '../test/cfg/settings/settings_old_version.json'

        print("Launching backend...")
        process = subprocess.Popen(
            shlex.split('python ../alignak_backend/main.py'),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print('PID = ', process.pid)
        time.sleep(1)

        ret = process.poll()
        if ret is not None:
            for line in iter(process.stdout.readline, b''):
                print("... " + line.rstrip())
            for line in iter(process.stderr.readline, b''):
                print("... " + line.rstrip())

        time.sleep(3)
        self._backend_clean()
        self._some_activity()
        time.sleep(3)

        print("Killing backend...")
        process.terminate()
        for line in iter(process.stdout.readline, b''):
            print(">>> " + str(line).rstrip())

        login = False
        for line in iter(process.stderr.readline, b''):
            print("*** " + str(line).rstrip())
            line = str(line)
            if 'POST /login HTTP/1.1' in line:
                login = True
        assert login
