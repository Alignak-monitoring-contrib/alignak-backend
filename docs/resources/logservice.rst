.. _resource-logservice:

logservice
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "state_type", "string", "", "HARD", ""
   "long_output", "string", "", "None", ""
   "state", "string", "", "UP", ""
   "output", "string", "", "None", ""
   "**service_description**", "**objectid**", "**True**", "****", "**:ref:`service <resource-service>`**"
   "acknowledged", "boolean", "", "False", ""
   "perf_data", "string", "", "None", ""
   "last_check", "integer", "", "None", ""
