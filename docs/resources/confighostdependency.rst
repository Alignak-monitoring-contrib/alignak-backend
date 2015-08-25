.. _resource-hostdependency:

hostdependency
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "inherits_parent", "boolean", "", "False", ""
   "notification_failure_criteria", "list", "", "['n']", ""
   "definition_order", "integer", "", "100", ""
   "dependent_host_name", "string", "", "", ""
   "dependent_hostgroup_name", "string", "", "", ""
   "imported_from", "string", "", "", ""
   "use", "objectid", "", "", ":ref:`hostdependency <resource-hostdependency>`"
   "name", "string", "", "", ""
   "dependency_period", "string", "", "", ""
   "execution_failure_criteria", "list", "", "['n']", ""
   "register", "boolean", "", "True", ""
   "hostgroup_name", "string", "", "unknown", ""
   "host_name", "string", "", "", ""
