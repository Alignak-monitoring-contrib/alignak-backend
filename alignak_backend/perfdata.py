#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provide classes to handle performance data from monitoring plugin output
"""
import re
from six import itervalues

PERFDATA_SPLIT_PATTERN = re.compile(r'([^=]+=\S+)')
METRIC_PATTERN = \
    re.compile(
        r'^([^=]+)=([\d\.\-\+eE]+)([\w\/%]*)'
        r';?([\d\.\-\+eE:~@]+)?;?([\d\.\-\+eE:~@]+)?;?([\d\.\-\+eE]+)?;?([\d\.\-\+eE]+)?;?\s*'
    )


def to_best_int_float(val):
    """Get best type for value between int and float

    :param val: value
    :type val:
    :return: int(float(val)) if int(float(val)) == float(val), else float(val)
    :rtype: int | float

    >>> to_best_int_float("20.1")
    20.1

    >>> to_best_int_float("20.0")
    20

    >>> to_best_int_float("20")
    20
    """
    integer = int(float(val))
    flt = float(val)
    # If the f is a .0 value,
    # best match is int
    if integer == flt:
        return integer
    return flt


def guess_int_or_float(val):
    """Wrapper for Util.to_best_int_float
    Basically cast into float or int and compare value
    If they are equal then there is no coma so return integer

    :param val: value to cast
    :return: value casted into int, float or None
    :rtype: int | float | NoneType
    """
    try:
        return to_best_int_float(val)
    except Exception:
        return None


class Metric(object):
    """
    Class providing a small abstraction for one metric of a Perfdatas class
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, string):
        self.name = self.value = self.uom = \
            self.warning = self.critical = self.min = self.max = None
        string = string.strip()
        matches = METRIC_PATTERN.match(string)
        if matches:
            # Get the name but remove all ' in it
            self.name = matches.group(1).replace("'", "")
            self.value = guess_int_or_float(matches.group(2))
            self.uom = matches.group(3)
            self.warning = guess_int_or_float(matches.group(4))
            self.critical = guess_int_or_float(matches.group(5))
            self.min = guess_int_or_float(matches.group(6))
            self.max = guess_int_or_float(matches.group(7))
            if self.uom == '%':
                self.min = 0
                self.max = 100

    def __str__(self):  # pragma: no cover, only for debugging purpose
        string = "%s=%s%s" % (self.name, self.value, self.uom)
        if self.warning is not None:
            string += ";%s" % (self.warning)
        else:
            string += ";"
        if self.critical is not None:
            string += ";%s" % (self.critical)
        else:
            string += ";"
        if self.min is not None:
            string += ";%s" % (self.min)
        else:
            string += ";"
        if self.max is not None:
            string += ";%s" % (self.max)
        else:
            string += ";"
        return string


class PerfDatas(object):
    """
    Class providing performance data extracted from a check output
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, string):
        string = string or ''
        elts = PERFDATA_SPLIT_PATTERN.findall(string)
        elts = [e for e in elts if e != '']
        self.metrics = {}
        for elem in elts:
            metric = Metric(elem)
            if metric.name is not None:
                self.metrics[metric.name] = metric

    def __iter__(self):  # pragma: no cover, not used internally
        return itervalues(self.metrics)

    def __len__(self):  # pragma: no cover, not used internally
        return len(self.metrics)

    def __getitem__(self, key):  # pragma: no cover, not used internally
        return self.metrics[key]

    def __contains__(self, key):  # pragma: no cover, not used internally
        return key in self.metrics
