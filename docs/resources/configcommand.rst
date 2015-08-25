.. _resource-command:

command
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "definition_order", "integer", "", "100", ""
   "reactionner_tag", "string", "", "None", ""
   "module_type", "string", "", "fork", ""
   "**command_name**", "**string**", "**True**", "****", "****"
   "use", "objectid", "", "", ":ref:`command <resource-command>`"
   "name", "string", "", "", ""
   "register", "boolean", "", "True", ""
   "**command_line**", "**string**", "**True**", "****", "****"
   "poller_tag", "string", "", "None", ""
   "timeout", "integer", "", "-1", ""
   "enable_environment_macros", "boolean", "", "False", ""
