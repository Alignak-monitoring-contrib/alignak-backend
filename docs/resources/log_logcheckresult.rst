.. _resource-logcheckresult:

Check result log (logcheckresult)
=================================


    The ``logcheckresult`` model is used to maintain a log of the received checks results.

    The Alignak backend stores all the checks results it receives to keep a full log of the system
    checks results.
    

.. image:: ../_static/log_logcheckresult.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| :ref:`_realm <logcheckresult-_realm>`
   | *Realm*", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "| :ref:`_sub_realm <logcheckresult-_sub_realm>`
   | *Sub-realms*", "boolean", "", "True", ""
   "| _users_read", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| acknowledged
   | *Acknowledged*", "boolean", "", "False", ""
   "| acknowledgement_type
   | *Acknowledgement type*", "integer", "", "1", ""
   "| downtimed
   | *Downtimed*", "boolean", "", "False", ""
   "| execution_time
   | *Execution time*", "float", "", "0.0", ""
   "| host
   | *Concerned host*", "**objectid**", "**True**", "****", ":ref:`host <resource-host>`"
   "| :ref:`host_name <logcheckresult-host_name>`
   | *Host name*", "string", "", "", ""
   "| last_check
   | *Check timestamp*", "integer", "", "0", ""
   "| :ref:`last_state <logcheckresult-last_state>`
   | *Last state*", "string", "", "OK", ""
   "| last_state_changed
   | *Last state changed*", "integer", "", "0", ""
   "| last_state_id
   | *Last state identifier*", "integer", "", "0", ""
   "| :ref:`last_state_type <logcheckresult-last_state_type>`
   | *Last state type*", "**string**", "**True**", "****", ""
   "| latency
   | *Latency*", "float", "", "0.0", ""
   "| long_output
   | *Long output*", "string", "", "", ""
   "| output
   | *Output*", "string", "", "", ""
   "| passive_check
   | *Passive check*", "boolean", "", "False", ""
   "| perf_data
   | *Performance data*", "string", "", "", ""
   "| :ref:`service <logcheckresult-service>`
   | *Concerned service*", "**objectid**", "**True**", "****", ":ref:`service <resource-service>`"
   "| :ref:`service_name <logcheckresult-service_name>`
   | *Service name*", "string", "", "", ""
   "| :ref:`state <logcheckresult-state>`
   | *State*", "**string**", "**True**", "****", ""
   "| state_changed
   | *State changed*", "boolean", "", "False", ""
   "| state_id
   | *State identifier*", "integer", "", "0", ""
   "| :ref:`state_type <logcheckresult-state_type>`
   | *State type*", "**string**", "**True**", "****", ""
.. _logcheckresult-_realm:

``_realm``: Realm this element belongs to.

.. _logcheckresult-_sub_realm:

``_sub_realm``: Is this element visible in the sub-realms of its realm?

.. _logcheckresult-host_name:

``host_name``: The backend stores the host name. This allows to keep an information about the concerned host even if it has been deleted from the backend.

.. _logcheckresult-last_state:

``last_state``: 

   Allowed values: [, ', O, K, ', ,,  , ', W, A, R, N, I, N, G, ', ,,  , ', C, R, I, T, I, C, A, L, ', ,,  , ', U, N, K, N, O, W, N, ', ,,  , ', U, P, ', ,,  , ', D, O, W, N, ', ,,  , ', U, N, R, E, A, C, H, A, B, L, E, ', ]

.. _logcheckresult-last_state_type:

``last_state_type``: 

   Allowed values: [, ', H, A, R, D, ', ,,  , ', S, O, F, T, ', ]

.. _logcheckresult-service:

``service``: If not set, this check result is an host check

.. _logcheckresult-service_name:

``service_name``: The backend stores the service name. This allows to keep an information about the concerned service even if it has been deleted from the backend.

.. _logcheckresult-state:

``state``: 

   Allowed values: [, ', U, P, ', ,,  , ', D, O, W, N, ', ,,  , ', U, N, R, E, A, C, H, A, B, L, E, ', ,,  , ', O, K, ', ,,  , ', W, A, R, N, I, N, G, ', ,,  , ', C, R, I, T, I, C, A, L, ', ,,  , ', U, N, K, N, O, W, N, ', ]

.. _logcheckresult-state_type:

``state_type``: 

   Allowed values: [, ', H, A, R, D, ', ,,  , ', S, O, F, T, ', ]



