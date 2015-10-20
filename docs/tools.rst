.. _tools:

Tools
=====

With the backend, some tools have been added and can help you in some cases.

cfg_to_backend
--------------

 `cfg_to_backend` is an utility tool that can import a monitoring configuration stored in flat files
and send this configuration to Alignak backend. It allows importing an existing configuration from
Nagios or Shinken.

 Command line interface::

   Usage:
       {command} [-h] [-v] [-d] [-b=backend] [-u=username] [-p=password] <cfg_file> ...
       {command} -h
       {command} -v

   Options:
       -h, --help                  Show this screen.
       -v, --version               Show application version.
       -b, --backend url           Specify backend URL [default: http://127.0.0.1:5000]
       -d, --delete                Delete existing backend data
       -u, --username username     Backend login username [default: admin]
       -p, --password password     Backend login password [default: admin]


 The default behavior is to update an existing backend on running on http://127.0.0.1:5000. This is
why it does not delete the existing backend content. To start a new backend from scratch, please
specify `--delete`.

* cfg_to_backend.py_: script to open cfg files (alignak, nagios, shinken) and send config to the backend

.. _cfg_to_backend.py: https://github.com/Alignak-monitoring-contrib/alignak-backend/blob/master/tools/cfg_to_backend.py
