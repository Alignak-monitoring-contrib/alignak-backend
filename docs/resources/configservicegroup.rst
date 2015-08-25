.. _resource-servicegroup:

servicegroup
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "**servicegroup_name**", "**string**", "**True**", "****", "****"
   "notes", "string", "", "", ""
   "alias", "string", "", "", ""
   "action_url", "string", "", "", ""
   "notes_url", "string", "", "", ""
   "members", "objectid", "", "", ":ref:`contact <resource-contact>`"
   "servicegroup_members", "list of objectid", "", "", ":ref:`servicegroup <resource-servicegroup>`"
