.. _resource-influxdb:

influxdb
===================

.. image:: ../_static/configinfluxdb.png


.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "_users_update", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "**address**", "**string**", "**True**", "****", ""
   "**password**", "**string**", "**True**", "****", ""
   "port", "integer", "", "8086", ""
   "prefix", "string", "", "", ""
   "**_realm**", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "**name**", "**string**", "**True**", "****", ""
   "**database**", "**string**", "**True**", "**alignak**", ""
   "grafana", "objectid", "", "None", ":ref:`grafana <resource-grafana>`"
   "_users_delete", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "_sub_realm", "boolean", "", "False", ""
   "**login**", "**string**", "**True**", "****", ""

