.. automodule:: epc


EPC server API
==============

Server
------

.. py:module:: epc.server

.. inheritance-diagram::
   EPCServer
   :parts: 1

.. autoclass:: EPCServer
   :no-members:

   .. automethod:: register_function
   .. automethod:: register_instance
   .. automethod:: set_debugger
   .. automethod:: print_port

   .. py:attribute:: clients
      :annotation: = []

      A list of :py:class:`EPCHandler` object for connected clients.

   .. automethod:: handle_client_connect
   .. automethod:: handle_client_disconnect

.. autoclass:: ThreadingEPCServer


Handler
-------

.. inheritance-diagram::
   EPCHandler
   :parts: 1

.. autoclass:: EPCHandler


EPC client API
==============

.. py:module:: epc.client

.. inheritance-diagram::
   EPCClient
   :parts: 1

.. autoclass:: EPCClient
   :no-members:

   .. automethod:: connect
   .. automethod:: close


EPC exceptions
==============

.. py:module:: epc.handler

.. inheritance-diagram::
   EPCErrorCallerUnknown
   ReturnErrorCallerUnknown
   :parts: 1

.. autoclass:: BaseRemoteError
.. autoclass:: CallerUnknown
.. autoclass:: EPCError
.. autoclass:: ReturnError
.. autoclass:: EPCErrorCallerUnknown
.. autoclass:: ReturnErrorCallerUnknown


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
