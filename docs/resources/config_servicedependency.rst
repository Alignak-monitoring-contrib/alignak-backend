.. _resource-servicedependency:

Service dependency (servicedependency)
======================================


    The ``servicedependency`` model is used to define dependency relations and tests conditions.

    See the Alignak documentation regarding the dependency check management.
    

.. image:: ../_static/config_servicedependency.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| :ref:`_realm <servicedependency-_realm>`
   | *Realm*", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "| :ref:`_sub_realm <servicedependency-_sub_realm>`
   | *Sub-realms*", "boolean", "", "True", ""
   "| _users_delete", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_read", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_update", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| :ref:`alias <servicedependency-alias>`
   | *Alias*", "string", "", "", ""
   "| :ref:`definition_order <servicedependency-definition_order>`
   | *Definition order*", "integer", "", "100", ""
   "| :ref:`dependency_period <servicedependency-dependency_period>`
   | *Dependency period*", "**objectid**", "**True**", "****", ":ref:`timeperiod <resource-timeperiod>`"
   "| :ref:`dependent_hostgroups <servicedependency-dependent_hostgroups>`
   | *Dependent hosts groups*", "objectid list", "", "", ":ref:`hostgroup <resource-hostgroup>`"
   "| :ref:`dependent_hosts <servicedependency-dependent_hosts>`
   | *Dependent hosts*", "objectid list", "", "", ":ref:`host <resource-host>`"
   "| :ref:`dependent_services <servicedependency-dependent_services>`
   | *Dependent services*", "objectid list", "", "", ":ref:`service <resource-service>`"
   "| :ref:`execution_failure_criteria <servicedependency-execution_failure_criteria>`
   | *Execution criteria*", "list", "", "['u', 'c', 'w']", ""
   "| explode_hostgroup", "boolean", "", "False", ""
   "| :ref:`hostgroups <servicedependency-hostgroups>`
   | *Hosts groups*", "objectid list", "", "", ":ref:`hostgroup <resource-hostgroup>`"
   "| :ref:`hosts <servicedependency-hosts>`
   | *Hosts*", "objectid list", "", "", ":ref:`host <resource-host>`"
   "| :ref:`imported_from <servicedependency-imported_from>`
   | *Imported from*", "string", "", "unknown", ""
   "| :ref:`inherits_parent <servicedependency-inherits_parent>`
   | *Parent inheritance*", "boolean", "", "False", ""
   "| name
   | *Service dependency name*", "string", "", "", ""
   "| :ref:`notes <servicedependency-notes>`
   | *Notes*", "string", "", "", ""
   "| :ref:`notification_failure_criteria <servicedependency-notification_failure_criteria>`
   | *Notification criteria*", "list", "", "['u', 'c', 'w']", ""
   "| schema_version", "integer", "", "1", ""
   "| :ref:`services <servicedependency-services>`
   | *Services*", "objectid list", "", "", ":ref:`service <resource-service>`"
.. _servicedependency-_realm:

``_realm``: Realm this element belongs to.

.. _servicedependency-_sub_realm:

``_sub_realm``: Is this element visible in the sub-realms of its realm?

.. _servicedependency-alias:

``alias``: Element friendly name used by the Web User Interface.

.. _servicedependency-definition_order:

``definition_order``: Priority level if several elements have the same name

.. _servicedependency-dependency_period:

``dependency_period``: Time period during which the dependency checks are done.

.. _servicedependency-dependent_hostgroups:

``dependent_hostgroups``: List of the hosts groups that are depending.

.. _servicedependency-dependent_hosts:

``dependent_hosts``: List of the hosts that are depending.

.. _servicedependency-dependent_services:

``dependent_services``: List of the services that are depending.

.. _servicedependency-execution_failure_criteria:

``execution_failure_criteria``: See Alginak doc about dependency checks.

   Allowed values: ['o', 'w', 'u', 'c', 'p', 'n']

.. _servicedependency-hostgroups:

``hostgroups``: List of the hosts groups involved in the dependency.

.. _servicedependency-hosts:

``hosts``: List of the hosts involved in the dependency.

.. _servicedependency-imported_from:

``imported_from``: Item importation source (alignak-backend-import, ...)

.. _servicedependency-inherits_parent:

``inherits_parent``: See Alginak doc about dependency checks.

.. _servicedependency-notes:

``notes``: Element notes. Free text to store element information.

.. _servicedependency-notification_failure_criteria:

``notification_failure_criteria``: See Alginak doc about dependency checks.

   Allowed values: ['o', 'w', 'u', 'c', 'p', 'n']

.. _servicedependency-services:

``services``: List of the services involved in the dependency.



