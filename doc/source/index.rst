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

   .. automethod:: EPCDispacher.register_function

.. autoclass:: EPCClientManager

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

.. autoclass:: BaseEPCError
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
