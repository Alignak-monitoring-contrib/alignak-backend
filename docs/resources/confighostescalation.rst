.. _resource-hostescalation:

hostescalation
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "_users_update", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "usergroups", "list of objectid", "", "", ":ref:`usergroup <resource-usergroup>`"
   "**name**", "**string**", "**True**", "****", ""
   "definition_order", "integer", "", "100", ""
   "_sub_realm", "boolean", "", "False", ""
   "last_notification_time", "integer", "", "", ""
   "notes", "string", "", "", ""
   "hostgroup", "list of objectid", "", "", ":ref:`hostgroup <resource-hostgroup>`"
   "notification_interval", "integer", "", "30", ""
   "_users_delete", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "alias", "string", "", "", ""
   "host", "objectid", "", "", ":ref:`host <resource-host>`"
   "**escalation_period**", "**objectid**", "**True**", "****", ":ref:`timeperiod <resource-timeperiod>`"
   "**_realm**", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "first_notification_time", "integer", "", "", ""
   "first_notification", "integer", "", "", ""
   "last_notification", "integer", "", "", ""
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "escalation_options", "list", "", "['d', 'u', 'r', 'w', 'c']", ""
   "imported_from", "string", "", "unknown", ""
   "users", "list of objectid", "", "", ":ref:`user <resource-user>`"

.. image:: resources/confighostescalation.png
