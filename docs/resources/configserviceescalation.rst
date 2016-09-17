.. _resource-serviceescalation:

serviceescalation
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "_users_update", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "first_notification", "integer", "", "", ""
   "hostgroups", "list of objectid", "", "", ":ref:`hostgroup <resource-hostgroup>`"
   "service", "objectid", "", "", ":ref:`service <resource-service>`"
   "last_notification", "integer", "", "", ""
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "**_realm**", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "usergroups", "list of objectid", "", "", ":ref:`usergroup <resource-usergroup>`"
   "notification_interval", "integer", "", "30", ""
   "last_notification_time", "integer", "", "", ""
   "_users_delete", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "_sub_realm", "boolean", "", "False", ""
   "users", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "definition_order", "integer", "", "100", ""
   "host", "objectid", "", "", ":ref:`host <resource-host>`"
   "**escalation_period**", "**objectid**", "**True**", "****", ":ref:`timeperiod <resource-timeperiod>`"
   "imported_from", "string", "", "unknown", ""
   "**name**", "**string**", "**True**", "****", ""
   "notes", "string", "", "", ""
   "alias", "string", "", "", ""
   "first_notification_time", "integer", "", "", ""
   "escalation_options", "list", "", "['d', 'u', 'r', 'w', 'c']", ""

.. image:: resources/configserviceescalation.png
