.. _resource-timeperiod:

Alignak time period (timeperiod)
================================


    The ``timeperiod`` model is used to represent time periods in the monitored system.

    Time periods are used in many situations:

    - for the hosts and services active/passive checks. Outside of the defined time periods,
    Alignak will not try to determine the hosts/services states.

    - for the notifications. The notifications will be sent-out only during the defined
    time periods.

    A time period is built with time ranges for each day of the week that "rotate" once the
    week has ended. Different types of exceptions to the normal weekly time are supported,
    including: specific weekdays, days of generic months, days of specific months,
    and calendar dates.
    

.. image:: ../_static/config_timeperiod.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| :ref:`_realm <timeperiod-_realm>`
   | *Realm*", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "| :ref:`_sub_realm <timeperiod-_sub_realm>`
   | *Sub-realms*", "boolean", "", "True", ""
   "| _users_delete", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_read", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_update", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| :ref:`alias <timeperiod-alias>`
   | *Alias*", "string", "", "", ""
   "| :ref:`dateranges <timeperiod-dateranges>`
   | *Date ranges*", "list", "", "[]", ""
   "| :ref:`definition_order <timeperiod-definition_order>`
   | *Definition order*", "integer", "", "100", ""
   "| :ref:`exclude <timeperiod-exclude>`
   | *Exclusions*", "list", "", "[]", ""
   "| :ref:`imported_from <timeperiod-imported_from>`
   | *Imported from*", "string", "", "unknown", ""
   "| :ref:`is_active <timeperiod-is_active>`
   | *Active*", "boolean", "", "False", ""
   "| :ref:`name <timeperiod-name>`
   | *Time period name*", "**string**", "**True**", "****", ""
   "| :ref:`notes <timeperiod-notes>`
   | *Notes*", "string", "", "", ""
   "| schema_version", "integer", "", "1", ""
.. _timeperiod-_realm:

``_realm``: Realm this element belongs to.

.. _timeperiod-_sub_realm:

``_sub_realm``: Is this element visible in the sub-realms of its realm?

.. _timeperiod-alias:

``alias``: Element friendly name used by the Web User Interface.

.. _timeperiod-dateranges:

``dateranges``: List of date ranges

.. _timeperiod-definition_order:

``definition_order``: Priority level if several elements have the same name

.. _timeperiod-exclude:

``exclude``: List of excluded ranges.

.. _timeperiod-imported_from:

``imported_from``: Item importation source (alignak-backend-import, ...)

.. _timeperiod-is_active:

``is_active``: The timeperiod is currently active or inactive.

.. _timeperiod-name:

``name``: Unique time period name

.. _timeperiod-notes:

``notes``: Element notes. Free text to store element information.



