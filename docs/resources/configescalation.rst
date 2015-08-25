.. _resource-escalation:

escalation
===================

.. csv-table::
   :header: "Parameter", "Type", "Required", "Default", "Data relation"

   "definition_order", "integer", "", "100", ""
   "escalation_name", "string", "", "", ""
   "contact_groups", "list of objectid", "", "", ":ref:`contactgroup <resource-contactgroup>`"
   "escalation_period", "string", "", "", ""
   "last_notification", "integer", "", "0", ""
   "imported_from", "string", "", "", ""
   "use", "objectid", "", "", ":ref:`escalation <resource-escalation>`"
   "name", "string", "", "", ""
   "notification_interval", "integer", "", "-1", ""
   "contacts", "list of objectid", "", "", ":ref:`contact <resource-contact>`"
   "last_notification_time", "integer", "", "0", ""
   "escalation_options", "list", "", "['d', 'u', 'r', 'w', 'c']", ""
   "register", "boolean", "", "True", ""
   "first_notification_time", "integer", "", "0", ""
   "first_notification", "integer", "", "0", ""
