.. _resource-hostdependency:

hostdependency
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "inherits_parent", "boolean", "", "False", ""
   "_users_update", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "notification_failure_criteria", "list", "", "['n']", ""
   "**name**", "**string**", "**True**", "****", "****"
   "definition_order", "integer", "", "100", ""
   "_sub_realm", "boolean", "", "False", ""
   "**dependency_period**", "**objectid**", "**True**", "****", "**:ref:`timeperiod <resource-timeperiod>`**"
   "execution_failure_criteria", "list", "", "['n']", ""
   "notes", "string", "", "", ""
   "hostgroups", "list of objectid", "", "", ":ref:`hostgroup <resource-hostgroup>`"
   "dependent_hostgroups", "list of objectid", "", "", ":ref:`hostgroup <resource-hostgroup>`"
   "_users_delete", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "alias", "string", "", "", ""
   "hosts", "list of objectid", "", "", ":ref:`host <resource-host>`"
   "**_realm**", "**objectid**", "**True**", "****", "**:ref:`realm <resource-realm>`**"
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "dependent_hosts", "list of objectid", "", "", ":ref:`host <resource-host>`"
   "imported_from", "string", "", "unknown", ""
