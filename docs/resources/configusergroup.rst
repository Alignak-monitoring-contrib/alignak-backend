.. _resource-usergroup:

usergroup
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "_users_update", "list of objectid", "", "[]", ":ref:`user <resource-user>`"
   "users", "list of objectid", "", "[]", ":ref:`user <resource-user>`"
   "definition_order", "integer", "", "100", ""
   "_users_read", "list of objectid", "", "[]", ":ref:`user <resource-user>`"
   "**_realm**", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "_level", "integer", "", "0", ""
   "usergroups", "list of objectid", "", "[]", ":ref:`usergroup <resource-usergroup>`"
   "**name**", "**string**", "**True**", "****", ""
   "_sub_realm", "boolean", "", "False", ""
   "notes", "string", "", "", ""
   "_parent", "objectid", "", "", ":ref:`usergroup <resource-usergroup>`"
   "alias", "string", "", "", ""
   "imported_from", "string", "", "unknown", ""
   "_tree_parents", "list of objectid", "", "[]", ":ref:`usergroup <resource-usergroup>`"
   "_users_delete", "list of objectid", "", "[]", ":ref:`user <resource-user>`"
