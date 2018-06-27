.. _resource-command:

Alignak command (command)
=========================


    The ``command`` model is used to represent a command in the monitored system.

    A command is used:

    - for the hosts and services active checks. The command is a check plugin
    used to determine the host or service state.

    - for the event handlers launched when an host / service state changes.

     - for the notifications sent to inform the users of the detected problems
    

.. image:: ../_static/config_command.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| :ref:`_realm <command-_realm>`
   | *Realm*", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "| :ref:`_sub_realm <command-_sub_realm>`
   | *Sub-realms*", "boolean", "", "True", ""
   "| _users_delete", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_read", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_update", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| :ref:`alias <command-alias>`
   | *Alias*", "string", "", "", ""
   "| :ref:`command_line <command-command_line>`
   | *Command line*", "string", "", "", ""
   "| :ref:`definition_order <command-definition_order>`
   | *Definition order*", "integer", "", "100", ""
   "| :ref:`enable_environment_macros <command-enable_environment_macros>`
   | *Environment macros*", "boolean", "", "False", ""
   "| :ref:`imported_from <command-imported_from>`
   | *Imported from*", "string", "", "unknown", ""
   "| :ref:`module_type <command-module_type>`
   | *Module type*", "string", "", "fork", ""
   "| :ref:`name <command-name>`
   | *Command name*", "**string**", "**True**", "****", ""
   "| :ref:`notes <command-notes>`
   | *Notes*", "string", "", "", ""
   "| :ref:`poller_tag <command-poller_tag>`
   | *Poller tag*", "string", "", "", ""
   "| :ref:`reactionner_tag <command-reactionner_tag>`
   | *Reactionner tag*", "string", "", "", ""
   "| schema_version", "integer", "", "1", ""
   "| :ref:`timeout <command-timeout>`
   | *Timeout*", "integer", "", "-1", ""
.. _command-_realm:

``_realm``: Realm this element belongs to.

.. _command-_sub_realm:

``_sub_realm``: Is this element visible in the sub-realms of its realm?

.. _command-alias:

``alias``: Element friendly name used by the Web User Interface.

.. _command-command_line:

``command_line``: System command executed to run the command.

.. _command-definition_order:

``definition_order``: Priority level if several elements have the same name

.. _command-enable_environment_macros:

``enable_environment_macros``: Set Alignak environment macros before running this command.

.. _command-imported_from:

``imported_from``: Item importation source (alignak-backend-import, ...)

.. _command-module_type:

``module_type``: A specific module type may be defined to associate commands to a dedicated worker. To be completed...

.. _command-name:

``name``: Unique command name

.. _command-notes:

``notes``: Element notes. Free text to store element information.

.. _command-poller_tag:

``poller_tag``: Set a value for this element checks to be managed by a dedicated poller.

.. _command-reactionner_tag:

``reactionner_tag``: Set a value for this element notifications to be managed by a dedicated reactionner.

.. _command-timeout:

``timeout``: Maximum command execution time before ALignak force the command stop.



