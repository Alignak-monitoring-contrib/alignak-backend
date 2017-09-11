.. _resource-livesynthesisretention:

LS history (livesynthesisretention)
===================================


    The ``livesynthesisretention`` model is a cache used internally by the backend to store the
    last computed live synthesis information. If the live synthesis history is configured,
    a count of ``SCHEDULER_LIVESYNTHESIS_HISTORY`` live synthesis elements will be store in the
    live synthesis retention data model.
    

.. image:: ../_static/ls_livesynthesisretention.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| hosts_acknowledged", "integer", "", "0", ""
   "| hosts_business_impact", "integer", "", "0", ""
   "| hosts_down_hard", "integer", "", "0", ""
   "| hosts_down_soft", "integer", "", "0", ""
   "| hosts_flapping", "integer", "", "0", ""
   "| hosts_in_downtime", "integer", "", "0", ""
   "| hosts_total", "integer", "", "0", ""
   "| hosts_unreachable_hard", "integer", "", "0", ""
   "| hosts_unreachable_soft", "integer", "", "0", ""
   "| hosts_up_hard", "integer", "", "0", ""
   "| hosts_up_soft", "integer", "", "0", ""
   "| livesynthesis", "**objectid**", "**True**", "****", ":ref:`livesynthesis <resource-livesynthesis>`"
   "| services_acknowledged", "integer", "", "0", ""
   "| services_business_impact", "integer", "", "0", ""
   "| services_critical_hard", "integer", "", "0", ""
   "| services_critical_soft", "integer", "", "0", ""
   "| services_flapping", "integer", "", "0", ""
   "| services_in_downtime", "integer", "", "0", ""
   "| services_ok_hard", "integer", "", "0", ""
   "| services_ok_soft", "integer", "", "0", ""
   "| services_total", "integer", "", "0", ""
   "| services_unknown_hard", "integer", "", "0", ""
   "| services_unknown_soft", "integer", "", "0", ""
   "| services_unreachable_hard", "integer", "", "0", ""
   "| services_unreachable_soft", "integer", "", "0", ""
   "| services_warning_hard", "integer", "", "0", ""
   "| services_warning_soft", "integer", "", "0", ""


