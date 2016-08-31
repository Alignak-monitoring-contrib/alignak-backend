.. _resource-servicegroup:

servicegroup
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "_level", "integer", "", "0", ""
   "_users_update", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "**name**", "**string**", "**True**", "****", "****"
   "definition_order", "integer", "", "100", ""
   "notes", "string", "", "", ""
   "_users_delete", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "services", "list of objectid", "", "", ":ref:`service <resource-service>`"
   "_parent", "objectid", "", "", ":ref:`servicegroup <resource-servicegroup>`"
   "alias", "string", "", "", ""
   "action_url", "string", "", "", ""
   "notes_url", "string", "", "", ""
   "**_realm**", "**objectid**", "**True**", "****", "**:ref:`realm <resource-realm>`**"
   "_tree_parents", "list of objectid", "", "[]", ":ref:`servicegroup <resource-servicegroup>`"
   "servicegroups", "list of objectid", "", "", ":ref:`servicegroup <resource-servicegroup>`"
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "imported_from", "string", "", "unknown", ""
