.. _resource-trigger:

trigger
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "_users_delete", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "alias", "string", "", "", ""
   "_users_update", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "code_src", "string", "", "", ""
   "**name**", "**string**", "**True**", "****", "****"
   "definition_order", "integer", "", "100", ""
   "**_realm**", "**objectid**", "**True**", "****", "**:ref:`realm <resource-realm>`**"
   "notes", "string", "", "", ""
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "imported_from", "string", "", "unknown", ""
