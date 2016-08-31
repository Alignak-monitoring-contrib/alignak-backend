.. _resource-livestate:

livestate
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "**service**", "**objectid**", "**True**", "****", "**:ref:`service <resource-service>`**"
   "next_check", "integer", "", "0", ""
   "_users_read", "list of objectid", "", "", ":ref:`user <resource-user>`"
   "**_realm**", "**objectid**", "**True**", "****", "**:ref:`realm <resource-realm>`**"
   "last_state", "string", "", "OK", ""
   "latency", "float", "", "0.0", ""
   "current_attempt", "integer", "", "0", ""
   "display_name_service", "string", "", "", ""
   "last_state_type", "string", "", "HARD", ""
   "state", "string", "", "OK", ""
   "display_name_host", "string", "", "", ""
   "type", "string", "", "host", ""
   "max_attempts", "integer", "", "0", ""
   "last_state_changed", "integer", "", "0", ""
   "execution_time", "float", "", "0.0", ""
   "last_check", "integer", "", "0", ""
   "state_type", "string", "", "HARD", ""
   "**host**", "**objectid**", "**True**", "****", "**:ref:`host <resource-host>`**"
   "downtime", "boolean", "", "False", ""
   "**name**", "**string**", "**True**", "****", "****"
   "acknowledged", "boolean", "", "False", ""
   "state_id", "integer", "", "0", ""
   "long_output", "string", "", "", ""
   "business_impact", "integer", "", "2", ""
   "output", "string", "", "", ""
   "perf_data", "string", "", "", ""
