.. _api:

Developer Interface
===================

This part of documentation is related of API REST for interact with this backend.
The examples in this part of documentation use :

* IP as 127.0.0.1
* a resource name as service

Get all resources available
---------------------------

All resources available in backend is available on root endpoint of backend::

    http://127.0.0.1:5000


Authentication in the backend
-----------------------------

The is an authentication system in the backend.

There are user accounts defined with *username*, *password* and *token*

To access to backend enpoints, you need the *token* associated to your account.

Get the token
~~~~~~~~~~~~~

Send POST method to *http://127.0.0.1:5000/login* with fields:

* *username*: xxx
* *password*: xxx

Example:

    curl -H "Content-Type: application/json" -X POST -d '{"username":"admin","password":"admin"}' http://127.0.0.1:5000/login

It will get for you the token.

Example of answer:

    {
        "token": "1442583814636-bed32565-2ff7-4023-87fb-34a3ac93d34c"
    }

Generate new token (so revoke old)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to generate a new token (mean revoke old token), add this field to the request made
when you get the token:

* *action*: *generate*

Example:

    curl -H "Content-Type: application/json" -X POST -d '{"username":"admin","password":"admin","action":"generate"}' http://127.0.0.1:5000/login


How to use the token
~~~~~~~~~~~~~~~~~~~~

For all method you request to endpoints, you need to pass the token.
Do pass this token, you can use *basic auth*. Pass token as username and set password empty.


GET method (get)
----------------

All items
~~~~~~~~~

The endpoint to get all items of a resource is::

    http://127.0.0.1:5000/service

The items will be in response in section *_items*.


~~~~~~~~~~~~~~~~~~~~~
All items + filtering
~~~~~~~~~~~~~~~~~~~~~

We can filter items to get with these syntax::

    http://127.0.0.1:5000/service?where={"service_description": "ping"}

~~~~~~~~~~~~~~~~~~~
All items + sorting
~~~~~~~~~~~~~~~~~~~

We can sorting items to get with these syntax::

    http://127.0.0.1:5000/service?sort=service_description

If you want to sort by descending::

    http://127.0.0.1:5000/service?sort=-service_description

~~~~~~~~~~~~~~~~~~~~
All items + embedded
~~~~~~~~~~~~~~~~~~~~

In this example, service resource has data relation with host resource with field *host_name*.
If you get items, you will have for this field an _id like *55d113976376e9835e1b2feb*

It's possible to have all fields of this host in same time with::

    http://127.0.0.1:5000/service?embedded={"host_name":1}

~~~~~~~~~~~~~~~~~~~~~~
All items + projection
~~~~~~~~~~~~~~~~~~~~~~

Projection is used to get only some fields of each items.
For example, to get only *service_description* of services::

    http://127.0.0.1:5000/service?projection={"service_description":1}

~~~~~~~~~~
Pagination
~~~~~~~~~~

The pagination is by default configured to 25 per request/page. It's possible to increase it to
the limit of 50 with::

    http://127.0.0.1:5000/service?max_results=50

In case of have many pages, in the items got, you have section::

    _links: {
        self: {
            href: "service",
            title: "service"
        },
        last: {
            href: "service?page=13",
            title: "last page"
        },
        parent: {
            href: "/",
            title: "home"
        },
        next: {
            href: "service?page=2",
            title: "next page"
        }
    },

So if you have _links/next, there is a next page.

~~~~~~~~~~~~~~~~
Meta information
~~~~~~~~~~~~~~~~

In the answer, you have a meta section::

    _meta: {
        max_results: 25,
        total: 309,
        page: 1
    }


One item
~~~~~~~~

To get only one item, we query with the *_id* in endpoint, like::

    http://127.0.0.1:5000/service/55d113976376e9835e1b3fee

It's possible in this case to use:

* projection_
* embedded_


.. _projection: #all-items-projection
.. _embedded: #all-items-embedded

POST method (add)
-----------------

This method is used to *create new item*.
It's required to use *POST* method for HTTP

You need to point to the endpoint of the resource like::

    http://127.0.0.1:5000/service

and send a JSON of data like::

    {"service_description":"ping","notification_interval":60}

If you want to add a relation with another resource, you must add the id of the resource, like::

    {"service_description":"ping","notification_interval":60,"host_name":"55d113976376e9835e1b2feb"}

You will receive a response with the new *_id* and the *_etag* like::

    {"_updated": "Tue, 25 Aug 2015 14:10:02 GMT", "_links": {"self": {"href": "service/55dc773a6376e90ac95f836f", "title": "Service"}}, "_created": "Tue, 25 Aug 2015 14:10:02 GMT", "_status": "OK", "_id": "55dc773a6376e90ac95f836f", "_etag": "3c996dc10cb86173fa79f807e0d84e88c2f3a28f"}


PATCH method (update)
---------------------

This method is used to *update fields* of an item.
It's required to use *PATCH* method for HTTP

You need to point to the item endpoint of the resource like::

    http://127.0.0.1:5000/service/55dc773a6376e90ac95f836f

You need to add in headers the *_etag* you have got when add or when you get data of this item::

    "If-Match: 3c996dc10cb86173fa79f807e0d84e88c2f3a28f"

and send a JSON of data like::

    {"service_description":"pong"}


DELETE method (delete)
----------------------

It's required to use *DELETE* method for HTTP

All items
~~~~~~~~~

The endpoint to delete all items of a resource is::

    http://127.0.0.1:5000/service

One item
~~~~~~~~

The endpoint to delete an item of a resource is::

    http://127.0.0.1:5000/service/55dc773a6376e90ac95f836f


More info about API
-------------------

When run the Alignak Backend, it exist an endpoint with API documentation::

    http://127.0.0.1:5000/docs

List of resources
-----------------

List of resources and information.


Configuration part
~~~~~~~~~~~~~~~~~~

List of resources used for configuration:

.. toctree::
   :maxdepth: 2
   :glob:

   resources/config*


Live state part
~~~~~~~~~~~~~~~

List of live states (last check date, current state...):

.. toctree::
   :maxdepth: 2
   :glob:

   resources/live*

Retention part
~~~~~~~~~~~~~~

List of retentions resources:

.. toctree::
   :maxdepth: 2
   :glob:

   resources/retention*

Log part
~~~~~~~~

List of log resources:

.. toctree::
   :maxdepth: 2
   :glob:

   resources/log*


