.. _resource-actiondowntime:

actiondowntime
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "comment", "string", "", "", ""
   "start_time", "integer", "", "0", ""
   "**host**", "**objectid**", "**True**", "****", ":ref:`host <resource-host>`"
   "**user**", "**objectid**", "**True**", "****", ":ref:`user <resource-user>`"
   "duration", "integer", "", "86400", ""
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "_realm", "objectid", "", "", ":ref:`realm <resource-realm>`"
   "**service**", "**objectid**", "**True**", "****", ":ref:`service <resource-service>`"
   "_sub_realm", "boolean", "", "False", ""
   "processed", "boolean", "", "False", ""
   "action", "string", "", "OK", ""
   "fixed", "boolean", "", "True", ""
   "end_time", "integer", "", "86400", ""

.. image:: resources/actiondowntime.png
