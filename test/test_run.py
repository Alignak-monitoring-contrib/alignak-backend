#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check is backend is running without error
"""

from __future__ import print_function

import os
import time
import shlex
import subprocess
import requests
import unittest2


class TestStart(unittest2.TestCase):
    """Test the different application start mode"""
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

    def test_start_application(self):
        """ Start application stand alone"""
        print('Launching application in dev mode')

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(os.path.join(dir_path, "../alignak_backend"))
        print("Launching application default...")
        process = subprocess.Popen(
            shlex.split('python ../alignak_backend/main.py')
        )
        print('PID = ', process.pid)
        time.sleep(3)

        headers = {'Content-Type': 'application/json'}
        params = {'username': 'admin', 'password': 'admin'}

        # Log onto the backend
        response = requests.post('http://127.0.0.1:5000/login', json=params, headers=headers)
        resp = response.json()
        assert resp['token']

        time.sleep(1)

        print("Killing application ...")
        process.terminate()

        # Restore initial path
        os.chdir(dir_path)

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
