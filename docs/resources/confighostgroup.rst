.. _resource-hostgroup:

hostgroup
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "**hostgroup_name**", "**string**", "**True**", "****", "****"
   "action_url", "string", "", "", ""
   "notes_url", "string", "", "", ""
   "members", "list of objectid", "", "", ":ref:`host <resource-host>`"
   "alias", "string", "", "", ""
   "realm", "string", "", "None", ""
   "hostgroup_members", "list of objectid", "", "", ":ref:`hostgroup <resource-hostgroup>`"
   "notes", "string", "", "", ""
