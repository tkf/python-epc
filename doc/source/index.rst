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


EPC exceptions
==============

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
