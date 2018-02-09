.. _resource-history:

Events log (history)
====================


    The ``history`` model is used to maintain a log of the received checks results.

    The Alignak backend stores all the checks results it receives to keep a full log of the system
    checks results.
    

.. image:: ../_static/log_history.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| _realm", "objectid", "", "", ":ref:`realm <resource-realm>`"
   "| _sub_realm", "boolean", "", "True", ""
   "| _users_read", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| :ref:`host <history-host>`
   | *Concerned host identifier*", "objectid", "", "", ":ref:`host <resource-host>`"
   "| :ref:`host_name <history-host_name>`
   | *Concerned host name*", "string", "", "", ""
   "| :ref:`logcheckresult <history-logcheckresult>`
   | *Relate log chek result (if any)*", "objectid", "", "", ":ref:`logcheckresult <resource-logcheckresult>`"
   "| message
   | *History event message*", "string", "", "", ""
   "| schema_version", "integer", "", "1", ""
   "| :ref:`service <history-service>`
   | *Concerned service identifier*", "objectid", "", "", ":ref:`service <resource-service>`"
   "| :ref:`service_name <history-service_name>`
   | *Concerned service name*", "string", "", "", ""
   "| :ref:`type <history-type>`
   | *History event type*", "**string**", "**True**", "**check.result**", ""
   "| :ref:`user <history-user>`
   | *Concerned user identifier*", "objectid", "", "", ":ref:`user <resource-user>`"
   "| :ref:`user_name <history-user_name>`
   | *Concerned user name*", "string", "", "", ""
.. _history-host:

``host``: ! Will be removed in a future version

.. _history-host_name:

``host_name``: The backend stores the host name. This allows to keep an information about the concerned host even if it has been deleted from the backend.

.. _history-logcheckresult:

``logcheckresult``: This relation is only valid if the event type is a check result

.. _history-service:

``service``: ! Will be removed in a future version

.. _history-service_name:

``service_name``: The backend stores the service name. This allows to keep an information about the concerned service even if it has been deleted from the backend.

.. _history-type:

``type``: 

   Allowed values: [, ', w, e, b, u, i, ., c, o, m, m, e, n, t, ', ,,  , ', c, h, e, c, k, ., r, e, s, u, l, t, ', ,,  , ', c, h, e, c, k, ., r, e, q, u, e, s, t, ', ,,  , ', c, h, e, c, k, ., r, e, q, u, e, s, t, e, d, ', ,,  , ', a, c, k, ., a, d, d, ', ,,  , ', a, c, k, ., p, r, o, c, e, s, s, e, d, ', ,,  , ', a, c, k, ., d, e, l, e, t, e, ', ,,  , ', d, o, w, n, t, i, m, e, ., a, d, d, ', ,,  , ', d, o, w, n, t, i, m, e, ., p, r, o, c, e, s, s, e, d, ', ,,  , ', d, o, w, n, t, i, m, e, ., d, e, l, e, t, e, ', ,,  , ', m, o, n, i, t, o, r, i, n, g, ., e, x, t, e, r, n, a, l, _, c, o, m, m, a, n, d, ', ,,  , ', m, o, n, i, t, o, r, i, n, g, ., t, i, m, e, p, e, r, i, o, d, _, t, r, a, n, s, i, t, i, o, n, ', ,,  , ', m, o, n, i, t, o, r, i, n, g, ., a, l, e, r, t, ', ,,  , ', m, o, n, i, t, o, r, i, n, g, ., e, v, e, n, t, _, h, a, n, d, l, e, r, ', ,,  , ', m, o, n, i, t, o, r, i, n, g, ., f, l, a, p, p, i, n, g, _, s, t, a, r, t, ', ,,  , ', m, o, n, i, t, o, r, i, n, g, ., f, l, a, p, p, i, n, g, _, s, t, o, p, ', ,,  , ', m, o, n, i, t, o, r, i, n, g, ., d, o, w, n, t, i, m, e, _, s, t, a, r, t, ', ,,  , ', m, o, n, i, t, o, r, i, n, g, ., d, o, w, n, t, i, m, e, _, c, a, n, c, e, l, l, e, d, ', ,,  , ', m, o, n, i, t, o, r, i, n, g, ., d, o, w, n, t, i, m, e, _, e, n, d, ', ,,  , ', m, o, n, i, t, o, r, i, n, g, ., a, c, k, n, o, w, l, e, d, g, e, ', ,,  , ', m, o, n, i, t, o, r, i, n, g, ., n, o, t, i, f, i, c, a, t, i, o, n, ', ]

.. _history-user:

``user``: ! Will be removed in a future version

.. _history-user_name:

``user_name``: The backend stores the user name. This allows to keep an information about the concerned user even if it has been deleted from the backend.



