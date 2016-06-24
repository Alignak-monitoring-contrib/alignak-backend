.. _resource-command:

command
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "_users_update", "list of objectid", "", "[]", ":ref:`user <resource-user>`"
   "**name**", "**string**", "**True**", "****", "****"
   "definition_order", "integer", "", "100", ""
   "poller_tag", "string", "", "None", ""
   "_sub_realm", "boolean", "", "False", ""
   "notes", "string", "", "", ""
   "command_line", "string", "", "", ""
   "_users_delete", "list of objectid", "", "[]", ":ref:`user <resource-user>`"
   "alias", "string", "", "", ""
   "reactionner_tag", "string", "", "None", ""
   "module_type", "string", "", "fork", ""
   "**_realm**", "**objectid**", "**True**", "****", "**:ref:`realm <resource-realm>`**"
   "timeout", "integer", "", "-1", ""
   "_users_read", "list of objectid", "", "[]", ":ref:`user <resource-user>`"
   "enable_environment_macros", "boolean", "", "False", ""
   "imported_from", "string", "", "unknown", ""
