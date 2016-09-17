.. _resource-timeperiod:

timeperiod
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "_users_update", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "definition_order", "integer", "", "100", ""
   "is_active", "boolean", "", "False", ""
   "exclude", "list", "", "[]", ""
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "**_realm**", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "_users_delete", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "**name**", "**string**", "**True**", "****", ""
   "_sub_realm", "boolean", "", "True", ""
   "notes", "string", "", "", ""
   "dateranges", "list", "", "[]", ""
   "alias", "string", "", "", ""
   "imported_from", "string", "", "unknown", ""

.. image:: resources/configtimeperiod.png
