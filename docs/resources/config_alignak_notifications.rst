.. _resource-alignak_notifications:

Alignak notifications (alignak_notifications)
=============================================


    The ``alignak_notifications`` model is a cache used internally by the backend to store the
    notifications that must be sent out to the Alignak arbiter.
    

.. image:: ../_static/config_alignak_notifications.png


.. csv-table:: Properties
   :header: "Property", "Type", "Required", "Default", "Relation"

   "| event
   | *Notification event (creation, deletion,...)*", "**string**", "**True**", "****", ""
   "| notification
   | *Notification url*", "string", "", "backend_notification", ""
   "| parameters
   | *Notification parameters*", "string", "", "", ""
   "| schema_version", "integer", "", "1", ""


