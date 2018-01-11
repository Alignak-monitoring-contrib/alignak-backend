#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check the models definition
"""

from __future__ import print_function
import unittest2
from alignak_backend.models import register_models


class TestModels(unittest2.TestCase):
    """
    This class test the models definition
    """

    def test_schema_version(self):
        """
        Test each fields on all models have a schema_version field

        :return: None
        """
        allmodels = register_models()
        for model_name in allmodels:
            print("Model: %s" % model_name)
            for field in allmodels[model_name]['schema']:
                print("- existing field: %s" % field)
                if field == 'schema_version':
                    assert 'schema_version' not in allmodels[model_name]['schema'][field]
                else:
                    assert 'schema_version' in allmodels[model_name]['schema'][field]
            for field in allmodels[model_name]['schema_deleted']:
                print("- deleted field: %s" % field)
                if field == 'schema_version':
                    assert 'schema_version' not in allmodels[model_name]['schema_deleted'][field]
                else:
                    assert 'schema_version' in allmodels[model_name]['schema_deleted'][field]

    def test_schema_version_uptodate(self):
        """
        Test the `schema_version` default value has the same value than the highest schema_version
        attribute value in fields of the model

        :return:
        """
        allmodels = register_models()
        for model_name in allmodels:
            print("Model: %s" % model_name)
            highest = 0
            for field in allmodels[model_name]['schema']:
                print("- existing field: %s" % field)
                if field != 'schema_version':
                    if allmodels[model_name]['schema'][field]['schema_version'] > highest:
                        highest = allmodels[model_name]['schema'][field]['schema_version']
            for field in allmodels[model_name]['schema_deleted']:
                print("- deleted field: %s" % field)
                if field != 'schema_version':
                    if allmodels[model_name]['schema_deleted'][field]['schema_version'] > highest:
                        highest = allmodels[model_name]['schema_deleted'][field]['schema_version']
            assert highest == allmodels[model_name]['schema']['schema_version']['default']
