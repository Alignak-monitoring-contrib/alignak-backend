.. _resource-userrestrictrole:

User role restriction (userrestrictrole)
========================================


    The ``userrestrictrole`` model is an internal data model used to define the CRUD
    rights for an Alignak backend user.

    This allows to defined, for a user and a given realm, the create, read, update, and
    delete rights on each backend endpoint.
    

.. image:: ../_static/userrestrictrole.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| :ref:`crud <userrestrictrole-crud>`
   | *Right*", "list", "", "['read']", ""
   "| realm
   | *Concerned realm*", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "| :ref:`resource <userrestrictrole-resource>`
   | *Concerned resource*", "string", "", "*", ""
   "| :ref:`sub_realm <userrestrictrole-sub_realm>`
   | *Sub-realms*", "boolean", "", "False", ""
   "| user
   | *Concerned user*", "**objectid**", "**True**", "****", ":ref:`user <resource-user>`"
.. _userrestrictrole-crud:

``crud``: User's right for the concerned resource in the concerned realm. Use ``*`` if all resources are concerned.

   Allowed values: create, read, update, delete, custom

.. _userrestrictrole-resource:

``resource``: Resource concerned with the right

   Allowed values: *, host, service, command

.. _userrestrictrole-sub_realm:

``sub_realm``: Is this right applicable to the sub-realms of the realm?



