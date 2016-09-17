.. _resource-hostgroup:

hostgroup
.. image:: _static/confighostgroup.png

===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "_level", "integer", "", "0", ""
   "_users_update", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "**name**", "**string**", "**True**", "****", ""
   "definition_order", "integer", "", "100", ""
   "_sub_realm", "boolean", "", "False", ""
   "_users_delete", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "notes", "string", "", "", ""
   "hostgroups", "list of objectid", "", "[]", ":ref:`hostgroup <resource-hostgroup>`"
   "_parent", "objectid", "", "", ":ref:`hostgroup <resource-hostgroup>`"
   "alias", "string", "", "", ""
   "action_url", "string", "", "", ""
   "notes_url", "string", "", "", ""
   "**_realm**", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "_tree_parents", "list of objectid", "", "[]", ":ref:`hostgroup <resource-hostgroup>`"
   "hosts", "list of objectid", "", "[]", ":ref:`host <resource-host>`"
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "imported_from", "string", "", "unknown", ""

