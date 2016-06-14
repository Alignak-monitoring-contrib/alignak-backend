#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Load resources schema
"""
import pkgutil
from importlib import import_module


def register_models():
    """
    Get all resources in files of this folder and return name + schema

    :return:
    """
    domain = {}
    files = pkgutil.walk_packages(path=__path__, prefix=__name__ + '.')
    for _, modname, _ in files:
        mod = import_module(modname)
        domain[mod.get_name()] = mod.get_schema()
    return domain
