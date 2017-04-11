.. _resource-hostescalation:

hostescalation
==============

.. image:: ../_static/confighostescalation.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| _realm", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "| _sub_realm", "boolean", "", "False", ""
   "| _users_delete", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_read", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_update", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| alias", "string", "", "", ""
   "| definition_order", "integer", "", "100", ""
   "| escalation_options", "list", "", "['d', 'u', 'r', 'w', 'c']", ""
   "| escalation_period", "**objectid**", "**True**", "****", ":ref:`timeperiod <resource-timeperiod>`"
   "| first_notification", "integer", "", "", ""
   "| first_notification_time", "integer", "", "", ""
   "| host", "objectid", "", "", ":ref:`host <resource-host>`"
   "| hostgroup", "objectid list", "", "", ":ref:`hostgroup <resource-hostgroup>`"
   "| imported_from", "string", "", "unknown", ""
   "| last_notification", "integer", "", "", ""
   "| last_notification_time", "integer", "", "", ""
   "| name", "**string**", "**True**", "****", ""
   "| notes", "string", "", "", ""
   "| notification_interval", "integer", "", "30", ""
   "| usergroups", "objectid list", "", "", ":ref:`usergroup <resource-usergroup>`"
   "| users", "objectid list", "", "", ":ref:`user <resource-user>`"


