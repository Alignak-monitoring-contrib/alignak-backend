.. _resource-hostescalation:

Host escalation (hostescalation)
================================


    The ``hostescalation`` model is used to define escalated notifications for the hosts.

    See the Alignak documentation regarding the escalations to discover all the features
    and the possibilities behind this Alignak feature.
    

.. image:: ../_static/confighostescalation.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| :ref:`_realm <hostescalation-_realm>`
   | *Realm*", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "| :ref:`_sub_realm <hostescalation-_sub_realm>`
   | *Sub-realms*", "boolean", "", "True", ""
   "| _users_delete", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_read", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_update", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| :ref:`alias <hostescalation-alias>`
   | *Alias*", "string", "", "", ""
   "| :ref:`definition_order <hostescalation-definition_order>`
   | *Definition order*", "integer", "", "100", ""
   "| :ref:`escalation_options <hostescalation-escalation_options>`
   | *Escalation options*", "list", "", "['d', 'x', 'r']", ""
   "| :ref:`escalation_period <hostescalation-escalation_period>`
   | *Escalation time period*", "objectid", "", "", ":ref:`timeperiod <resource-timeperiod>`"
   "| :ref:`first_notification <hostescalation-first_notification>`
   | *First notification count*", "integer", "", "", ""
   "| :ref:`first_notification_time <hostescalation-first_notification_time>`
   | *First notification time*", "integer", "", "60", ""
   "| :ref:`hostgroups <hostescalation-hostgroups>`
   | *Hosts groups*", "objectid list", "", "", ":ref:`hostgroup <resource-hostgroup>`"
   "| :ref:`hosts <hostescalation-hosts>`
   | *Hosts*", "objectid list", "", "", ":ref:`host <resource-host>`"
   "| :ref:`imported_from <hostescalation-imported_from>`
   | *Imported from*", "string", "", "unknown", ""
   "| :ref:`last_notification <hostescalation-last_notification>`
   | *Last notification count*", "integer", "", "", ""
   "| :ref:`last_notification_time <hostescalation-last_notification_time>`
   | *Last notification time*", "integer", "", "240", ""
   "| :ref:`name <hostescalation-name>`
   | *Host escalation name*", "**string**", "**True**", "****", ""
   "| :ref:`notes <hostescalation-notes>`
   | *Notes*", "string", "", "", ""
   "| :ref:`notification_interval <hostescalation-notification_interval>`
   | *Notifications interval*", "integer", "", "60", ""
   "| :ref:`usergroups <hostescalation-usergroups>`
   | *Escalation users groups*", "objectid list", "", "", ":ref:`usergroup <resource-usergroup>`"
   "| :ref:`users <hostescalation-users>`
   | *Escalation users*", "objectid list", "", "", ":ref:`user <resource-user>`"
.. _hostescalation-_realm:

``_realm``: Realm this element belongs to.

.. _hostescalation-_sub_realm:

``_sub_realm``: Is this element visible in the sub-realms of its realm?

.. _hostescalation-alias:

``alias``: Element friendly name used by the Web User Interface.

.. _hostescalation-definition_order:

``definition_order``: Priority level if several elements have the same name

.. _hostescalation-escalation_options:

``escalation_options``: List of the notifications types this escalation is concerned with. This escalation will be used only if the host is in one of the states specified in this property.

   Allowed values: [, ', d, ', ,,  , ', x, ', ,,  , ', r, ', ]

.. _hostescalation-escalation_period:

``escalation_period``: No escalation notifications will be sent-out except during this time period.

.. _hostescalation-first_notification:

``first_notification``: Nagios legacy. Number of the first notification this escalation will be used. **Note** that this property will be deprecated in favor of the ``first_notification_time``.

.. _hostescalation-first_notification_time:

``first_notification_time``: Duration in minutes before sending the first escalated notification.

.. _hostescalation-hostgroups:

``hostgroups``: List of the hosts groups concerned by the escalation.

.. _hostescalation-hosts:

``hosts``: List of the hosts concerned by the escalation.

.. _hostescalation-imported_from:

``imported_from``: Item importation source (alignak-backend-import, ...)

.. _hostescalation-last_notification:

``last_notification``: Nagios legacy. Number of the last notification this escalation will not be used anymore. **Note** that this property will be deprecated in favor of the ``last_notification_time``.

.. _hostescalation-last_notification_time:

``last_notification_time``: Duration in minutes before sending the last escalated notification. Escalated notifications will be sent-out between the first_notification_time and last_notification_time period.

.. _hostescalation-name:

``name``: Unique host escalation name

.. _hostescalation-notes:

``notes``: Element notes. Free text to store element information.

.. _hostescalation-notification_interval:

``notification_interval``: Number of minutes to wait before re-sending the escalated notifications if the problem is still present. If you set this value to 0, only one notification will be sent out.

.. _hostescalation-usergroups:

``usergroups``: List of the users groups concerned by this escalation.

.. _hostescalation-users:

``users``: List of the users concerned by this escalation.



