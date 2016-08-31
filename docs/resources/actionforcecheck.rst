.. _resource-actionforcecheck:

actionforcecheck
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "comment", "string", "", "", ""
   "_sub_realm", "boolean", "", "False", ""
   "**host**", "**objectid**", "**True**", "****", "**:ref:`host <resource-host>`**"
   "**user**", "**objectid**", "**True**", "****", "**:ref:`user <resource-user>`**"
   "**service**", "**objectid**", "**True**", "****", "**:ref:`service <resource-service>`**"
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "_realm", "objectid", "", "", ":ref:`realm <resource-realm>`"
   "processed", "boolean", "", "False", ""
