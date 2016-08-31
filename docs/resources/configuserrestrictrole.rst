.. _resource-userrestrictrole:

userrestrictrole
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "**crud**", "**string**", "**True**", "**read**", "****"
   "**resource**", "**string**", "**True**", "****", "****"
   "**realm**", "**objectid**", "**True**", "****", "**:ref:`realm <resource-realm>`**"
   "**user**", "**objectid**", "**True**", "****", "**:ref:`user <resource-user>`**"
   "sub_realm", "boolean", "", "False", ""
