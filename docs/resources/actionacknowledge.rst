.. _resource-actionacknowledge:

actionacknowledge
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "comment", "string", "", "", ""
   "sticky", "boolean", "", "True", ""
   "**host**", "**objectid**", "**True**", "****", ":ref:`host <resource-host>`"
   "notify", "boolean", "", "False", ""
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "_realm", "objectid", "", "", ":ref:`realm <resource-realm>`"
   "**service**", "**objectid**", "**True**", "****", ":ref:`service <resource-service>`"
   "persistent", "boolean", "", "True", ""
   "_sub_realm", "boolean", "", "False", ""
   "processed", "boolean", "", "False", ""
   "action", "string", "", "OK", ""
   "**user**", "**objectid**", "**True**", "****", ":ref:`user <resource-user>`"
