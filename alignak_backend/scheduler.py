#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.scheduler`` module

    This module manages the scheduler jobs
"""
import alignak_backend.app


def cron_alignak():
    """
    It's the scheduler used to notify Alignak

    :return: None
    """
    alignak_backend.app.cron_alignak()


def cron_cache():
    """
    It's the scheduler used to send to graphite / influxdb retention perfdata if previously
    graphite / influxdb wasn't available

    :return: None
    """
    # test communication and see if data in cache
    alignak_backend.app.cron_timeseries()


def cron_grafana():
    """
    It's the scheduler used to update / create grafana dashboards

    :return: None
    """
    alignak_backend.app.cron_grafana()


def cron_livesynthesis_history():
    """
    It's the scheduler used to manage retention / history of livesynthesis

    :return: None
    """
    alignak_backend.app.cron_livesynthesis_history()
