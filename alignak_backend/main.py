#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main
"""

from alignak_backend.app import Application


def main():
    """
    Main function where application runs

    :return: None
    """
    app = Application()
    app.process_args()
