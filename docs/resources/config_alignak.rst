.. _resource-alignak:

Alignak configuration (alignak)
===============================


    The ``alignak`` model is used to store the global configuration of an Alignak instance.

    

.. image:: ../_static/config_alignak.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| _realm", "**objectid**", "**True**", "****", ":ref:`realm <resource-realm>`"
   "| _sub_realm", "boolean", "", "True", ""
   "| _users_delete", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_read", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| _users_update", "objectid list", "", "", ":ref:`user <resource-user>`"
   "| :ref:`accept_passive_host_checks <alignak-accept_passive_host_checks>`
   | *Passive host checks enabled*", "boolean", "", "True", ""
   "| :ref:`accept_passive_service_checks <alignak-accept_passive_service_checks>`
   | *Passive service checks enabled*", "boolean", "", "True", ""
   "| :ref:`additional_freshness_latency <alignak-additional_freshness_latency>`
   | *Additional freshness latency*", "integer", "", "15", ""
   "| :ref:`alias <alignak-alias>`
   | *Alias*", "string", "", "", ""
   "| :ref:`check_external_commands <alignak-check_external_commands>`
   | *Check external commands*", "boolean", "", "True", ""
   "| check_for_orphaned_hosts
   | *Check for orphaned hosts*", "boolean", "", "True", ""
   "| check_for_orphaned_services
   | *Check for orphaned services*", "boolean", "", "True", ""
   "| :ref:`check_host_freshness <alignak-check_host_freshness>`
   | *Host checks freshness check*", "boolean", "", "True", ""
   "| :ref:`check_service_freshness <alignak-check_service_freshness>`
   | *Passive service checks enabled*", "boolean", "", "True", ""
   "| :ref:`cleaning_queues_interval <alignak-cleaning_queues_interval>`
   | *Scheduler queues cleaning interval*", "integer", "", "900", ""
   "| :ref:`enable_environment_macros <alignak-enable_environment_macros>`
   | *Enable environment macros*", "boolean", "", "False", ""
   "| :ref:`enable_notifications <alignak-enable_notifications>`
   | *Notifications enabled*", "boolean", "", "True", ""
   "| :ref:`event_handler_timeout <alignak-event_handler_timeout>`
   | *Event handlers commands timeout*", "integer", "", "30", ""
   "| event_handlers_enabled
   | *Event handlers enabled*", "boolean", "", "True", ""
   "| execute_host_checks
   | *Active host checks enabled*", "boolean", "", "True", ""
   "| execute_service_checks
   | *Active service checks enabled*", "boolean", "", "True", ""
   "| flap_detection_enabled
   | *Flapping detection enabled*", "boolean", "", "True", ""
   "| :ref:`flap_history <alignak-flap_history>`
   | *Flapping history*", "integer", "", "20", ""
   "| :ref:`global_host_event_handler <alignak-global_host_event_handler>`
   | *Global host event handler*", "string", "", "None", ""
   "| :ref:`global_service_event_handler <alignak-global_service_event_handler>`
   | *Global service event handler*", "string", "", "None", ""
   "| high_host_flap_threshold
   | *Host high flapping threshold*", "integer", "", "30", ""
   "| high_service_flap_threshold
   | *Service high flapping threshold*", "integer", "", "30", ""
   "| :ref:`host_check_timeout <alignak-host_check_timeout>`
   | *Hosts checks commands timeout*", "integer", "", "30", ""
   "| :ref:`host_freshness_check_interval <alignak-host_freshness_check_interval>`
   | *Host freshness check interval*", "integer", "", "3600", ""
   "| :ref:`host_perfdata_command <alignak-host_perfdata_command>`
   | *Host performance data command*", "string", "", "None", ""
   "| illegal_macro_output_chars
   | *Illegal macros output characters*", "string", "", "", ""
   "| illegal_object_name_chars
   | *Illegal objects name characters*", "string", "", "`~!$%^&*'|'<>?,()=", ""
   "| :ref:`instance_id <alignak-instance_id>`
   | *Instance identifier*", "string", "", "", ""
   "| :ref:`instance_name <alignak-instance_name>`
   | *Instance name*", "string", "", "", ""
   "| :ref:`interval_length <alignak-interval_length>`
   | *Application interval length*", "integer", "", "60", ""
   "| :ref:`last_alive <alignak-last_alive>`
   | *Last time alive*", "integer", "", "0", ""
   "| :ref:`log_active_checks <alignak-log_active_checks>`
   | *Log objects active checks*", "boolean", "", "True", ""
   "| :ref:`log_event_handlers <alignak-log_event_handlers>`
   | *Log objects event handlers*", "boolean", "", "True", ""
   "| :ref:`log_external_commands <alignak-log_external_commands>`
   | *Log external commands*", "boolean", "", "True", ""
   "| :ref:`log_flappings <alignak-log_flappings>`
   | *Log objects states flapping*", "boolean", "", "True", ""
   "| :ref:`log_host_retries <alignak-log_host_retries>`
   | *Log hosts checks retries*", "boolean", "", "True", ""
   "| :ref:`log_initial_states <alignak-log_initial_states>`
   | *Log objects initial states*", "boolean", "", "True", ""
   "| :ref:`log_notifications <alignak-log_notifications>`
   | *Log notifications*", "boolean", "", "True", ""
   "| :ref:`log_passive_checks <alignak-log_passive_checks>`
   | *Log objects passive checks*", "boolean", "", "True", ""
   "| :ref:`log_service_retries <alignak-log_service_retries>`
   | *Log services checks retries*", "boolean", "", "True", ""
   "| :ref:`log_snapshots <alignak-log_snapshots>`
   | *Log objects snapshots*", "boolean", "", "True", ""
   "| low_host_flap_threshold
   | *Host low flapping threshold*", "integer", "", "20", ""
   "| low_service_flap_threshold
   | *Service low flapping threshold*", "integer", "", "20", ""
   "| :ref:`max_host_check_spread <alignak-max_host_check_spread>`
   | *Maximum hosts checks spread*", "integer", "", "30", ""
   "| :ref:`max_plugins_output_length <alignak-max_plugins_output_length>`
   | *Maximum check output length*", "integer", "", "8192", ""
   "| :ref:`max_service_check_spread <alignak-max_service_check_spread>`
   | *Maximum services checks spread*", "integer", "", "30", ""
   "| :ref:`name <alignak-name>`
   | *Alignak name*", "**string**", "**True**", "****", ""
   "| no_event_handlers_during_downtimes
   | *Event handlers launched when object is in a downtime period*", "boolean", "", "False", ""
   "| :ref:`notes <alignak-notes>`
   | *Notes*", "string", "", "", ""
   "| :ref:`notes_url <alignak-notes_url>`
   | *Notes URL*", "string", "", "", ""
   "| :ref:`notification_timeout <alignak-notification_timeout>`
   | *Notification commands timeout*", "integer", "", "30", ""
   "| :ref:`pid <alignak-pid>`
   | *Instance PID*", "integer", "", "0", ""
   "| :ref:`process_performance_data <alignak-process_performance_data>`
   | *Process performance data*", "boolean", "", "True", ""
   "| :ref:`program_start <alignak-program_start>`
   | *Program start time*", "integer", "", "0", ""
   "| schema_version", "integer", "", "1", ""
   "| :ref:`service_check_timeout <alignak-service_check_timeout>`
   | *Services checks commands timeout*", "integer", "", "60", ""
   "| :ref:`service_freshness_check_interval <alignak-service_freshness_check_interval>`
   | *Service freshness check interval*", "integer", "", "30", ""
   "| :ref:`service_perfdata_command <alignak-service_perfdata_command>`
   | *Service performance data command*", "string", "", "None", ""
   "| :ref:`timeout_exit_status <alignak-timeout_exit_status>`
   | *Command timeout exit status*", "integer", "", "2", ""
   "| use_timezone
   | *Alignak time zone*", "string", "", "", ""
.. _alignak-accept_passive_host_checks:

``accept_passive_host_checks``: Accept passive hosts checks. Default is True

.. _alignak-accept_passive_service_checks:

``accept_passive_service_checks``: Accept passive services checks

.. _alignak-additional_freshness_latency:

``additional_freshness_latency``: Extra time for the freshness check - default is 15 seconds

.. _alignak-alias:

``alias``: Element friendly name used by the Web User Interface.

.. _alignak-check_external_commands:

``check_external_commands``: Enable / disable the external commands management

.. _alignak-check_host_freshness:

``check_host_freshness``: Host checks freshness is enabled/disabled. Default is True

.. _alignak-check_service_freshness:

``check_service_freshness``: Accept passive services checks

.. _alignak-cleaning_queues_interval:

``cleaning_queues_interval``: Default is 15 minutes (900 seconds)

.. _alignak-enable_environment_macros:

``enable_environment_macros``: Enable to provide environment variables as macros to the launched commands. Default is disabled.

.. _alignak-enable_notifications:

``enable_notifications``: Raising notifications is enabled. Default is True

.. _alignak-event_handler_timeout:

``event_handler_timeout``: Default is 30 seconds

.. _alignak-flap_history:

``flap_history``: Number of states for flapping computing

.. _alignak-global_host_event_handler:

``global_host_event_handler``: Command that will be used as an event handler if none is specified for a specific host/service.

.. _alignak-global_service_event_handler:

``global_service_event_handler``: Command that will be used as an event handler if none is specified for a specific host/service.

.. _alignak-host_check_timeout:

``host_check_timeout``: Default is 30 seconds

.. _alignak-host_freshness_check_interval:

``host_freshness_check_interval``: Default is one hour (3600 seconds)

.. _alignak-host_perfdata_command:

``host_perfdata_command``: Command that will be run for the performance data of an host.

.. _alignak-instance_id:

``instance_id``: Reporting daemon identifier

.. _alignak-instance_name:

``instance_name``: Reporting daemon name

.. _alignak-interval_length:

``interval_length``: Default is 60 seconds for one minute

.. _alignak-last_alive:

``last_alive``: Date/time of this status report

.. _alignak-log_active_checks:

``log_active_checks``: Create a monitoring log event for this event

.. _alignak-log_event_handlers:

``log_event_handlers``: Create a monitoring log event for this event

.. _alignak-log_external_commands:

``log_external_commands``: Create a monitoring log event for this event

.. _alignak-log_flappings:

``log_flappings``: Create a monitoring log event for this event

.. _alignak-log_host_retries:

``log_host_retries``: Create a monitoring log event for this event

.. _alignak-log_initial_states:

``log_initial_states``: Create a monitoring log event for this event

.. _alignak-log_notifications:

``log_notifications``: Create a monitoring log event for this event

.. _alignak-log_passive_checks:

``log_passive_checks``: Create a monitoring log event for this event

.. _alignak-log_service_retries:

``log_service_retries``: Create a monitoring log event for this event

.. _alignak-log_snapshots:

``log_snapshots``: Create a monitoring log event for this event

.. _alignak-max_host_check_spread:

``max_host_check_spread``: Default is 30 seconds

.. _alignak-max_plugins_output_length:

``max_plugins_output_length``: Default is 8192 bytes

.. _alignak-max_service_check_spread:

``max_service_check_spread``: Default is 30 seconds

.. _alignak-name:

``name``: Alignak instance name. This will be compared to the Alignak arbiter instance name to get the correct configuration.

.. _alignak-notes:

``notes``: Element notes. Free text to store element information.

.. _alignak-notes_url:

``notes_url``: Element notes URL. Displayed in the Web UI as some URL to be navigatesd. Note that a very specific text format must be used for this field, see the Web UI documentation.

.. _alignak-notification_timeout:

``notification_timeout``: Default is 30 seconds

.. _alignak-pid:

``pid``: Reporting daemon PID

.. _alignak-process_performance_data:

``process_performance_data``: Enable / disable the performance data extra management

.. _alignak-program_start:

``program_start``: Date/time the Alignak scheduler started/restarted

.. _alignak-service_check_timeout:

``service_check_timeout``: Default is 60 seconds

.. _alignak-service_freshness_check_interval:

``service_freshness_check_interval``: Default is one hour (3600 seconds)

.. _alignak-service_perfdata_command:

``service_perfdata_command``: Command that will be run for the performance data of a service.

.. _alignak-timeout_exit_status:

``timeout_exit_status``: Default is 2 (CRITICAL)



