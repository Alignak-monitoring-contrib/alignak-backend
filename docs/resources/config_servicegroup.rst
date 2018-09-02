.. _resource-servicegroup:

Alignak services groups (servicegroup)
======================================


    The ``servicegroup`` model is used to group several hosts.

    

.. image:: ../_static/config_servicegroup.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| :ref:`_level <servicegroup-_level>`
   | *Level*", "integer", "", "0", ""
   "| :ref:`_parent <servicegroup-_parent>`
   | *Parent*", "objectid", "", "None", ":ref:`servicegroup <resource-servicegroup>`"
   "| :ref:`_realm <servicegroup-_realm>`
   | *Realm*", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "| :ref:`_sub_realm <servicegroup-_sub_realm>`
   | *Sub-realms*", "boolean", "", "True", ""
   "| :ref:`_tree_parents <servicegroup-_tree_parents>`
   | *Parents*", "objectid list", "", "[]", ":ref:`servicegroup <resource-servicegroup>`"
   "| _users_delete", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_read", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_update", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| :ref:`action_url <servicegroup-action_url>`
   | *Actions URL*", "string", "", "", ""
   "| :ref:`alias <servicegroup-alias>`
   | *Alias*", "string", "", "", ""
   "| :ref:`definition_order <servicegroup-definition_order>`
   | *Definition order*", "integer", "", "100", ""
   "| :ref:`imported_from <servicegroup-imported_from>`
   | *Imported from*", "string", "", "unknown", ""
   "| :ref:`name <servicegroup-name>`
   | *Services group name*", "**string**", "**True**", "****", ""
   "| :ref:`notes <servicegroup-notes>`
   | *Notes*", "string", "", "", ""
   "| :ref:`notes_url <servicegroup-notes_url>`
   | *Notes URL*", "string", "", "", ""
   "| schema_version", "integer", "", "1", ""
   "| :ref:`servicegroups <servicegroup-servicegroups>`
   | *Groups*", "objectid list", "", "[]", ":ref:`servicegroup <resource-servicegroup>`"
   "| :ref:`services <servicegroup-services>`
   | *Members*", "objectid list", "", "[]", ":ref:`service <resource-service>`"
.. _servicegroup-_level:

``_level``: Level in the hierarchy

.. _servicegroup-_parent:

``_parent``: Immediate parent in the hierarchy

.. _servicegroup-_realm:

``_realm``: Realm this element belongs to.

.. _servicegroup-_sub_realm:

``_sub_realm``: Is this element visible in the sub-realms of its realm?

.. _servicegroup-_tree_parents:

``_tree_parents``: List of parents in the hierarchy

.. _servicegroup-action_url:

``action_url``: Element actions URL. Displayed in the Web UI as some available actions. Note that a very specific text format must be used for this field, see the Web UI documentation.

.. _servicegroup-alias:

``alias``: Element friendly name used by the Web User Interface.

.. _servicegroup-definition_order:

``definition_order``: Priority level if several elements have the same name

.. _servicegroup-imported_from:

``imported_from``: Item importation source (alignak-backend-import, ...)

.. _servicegroup-name:

``name``: Unique services group name

.. _servicegroup-notes:

``notes``: Element notes. Free text to store element information.

.. _servicegroup-notes_url:

``notes_url``: Element notes URL. Displayed in the Web UI as some URL to be navigatesd. Note that a very specific text format must be used for this field, see the Web UI documentation.

.. _servicegroup-servicegroups:

``servicegroups``: List of the groups of this group

.. _servicegroup-services:

``services``: List of the members of this group



