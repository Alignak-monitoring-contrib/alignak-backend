.. _resource-history:

history
===================

.. image:: ../_static/confighistory.png


.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "logcheckresult", "objectid", "", "", ":ref:`logcheckresult <resource-logcheckresult>`"
   "service_name", "string", "", "", ""
   "host", "objectid", "", "", ":ref:`host <resource-host>`"
   "user", "objectid", "", "", ":ref:`user <resource-user>`"
   "message", "string", "", "", ""
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "_realm", "objectid", "", "", ":ref:`realm <resource-realm>`"
   "service", "objectid", "", "", ":ref:`service <resource-service>`"
   "user_name", "string", "", "", ""
   "_sub_realm", "boolean", "", "False", ""
   "host_name", "string", "", "", ""
   "**type**", "**string**", "**True**", "**check.result**", ""

