.. _resource-user:

user
.. image:: ../_static/configuser.png

===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "_users_update", "list of objectid", "", "[]", ":ref:`user <resource-user>`"
   "definition_order", "integer", "", "100", ""
   "tags", "list", "", "[]", ""
   "address1", "string", "", "", ""
   "service_notification_options", "list", "", "['w', 'u', 'c', 'r', 'f', 's']", ""
   "address3", "string", "", "", ""
   "address4", "string", "", "", ""
   "address5", "string", "", "", ""
   "address6", "string", "", "", ""
   "customs", "dict", "", "{}", ""
   "is_admin", "boolean", "", "False", ""
   "service_notifications_enabled", "boolean", "", "True", ""
   "can_submit_commands", "boolean", "", "False", ""
   "service_notification_commands", "list of objectid", "", "", ":ref:`command <resource-command>`"
   "pager", "string", "", "", ""
   "can_update_livestate", "boolean", "", "False", ""
   "imported_from", "string", "", "unknown", ""
   "notificationways", "list", "", "[]", ""
   "_users_read", "list of objectid", "", "[]", ":ref:`user <resource-user>`"
   "_users_delete", "list of objectid", "", "[]", ":ref:`user <resource-user>`"
   "password", "string", "", "NOPASSWORDSET", ""
   "**host_notification_period**", "**objectid**", "**True**", "****", ":ref:`timeperiod <resource-timeperiod>`"
   "**name**", "**string**", "**True**", "****", ""
   "host_notifications_enabled", "boolean", "", "True", ""
   "_sub_realm", "boolean", "", "False", ""
   "notes", "string", "", "", ""
   "host_notification_commands", "list of objectid", "", "", ":ref:`command <resource-command>`"
   "**service_notification_period**", "**objectid**", "**True**", "****", ":ref:`timeperiod <resource-timeperiod>`"
   "min_business_impact", "integer", "", "0", ""
   "address2", "string", "", "", ""
   "alias", "string", "", "", ""
   "token", "string", "", "", ""
   "**_realm**", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "ui_preferences", "dict", "", "{}", ""
   "back_role_super_admin", "boolean", "", "False", ""
   "email", "string", "", "", ""
   "host_notification_options", "list", "", "['d', 'u', 'r', 'f', 's']", ""

