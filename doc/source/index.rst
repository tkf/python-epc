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


Handler
-------

.. inheritance-diagram::
   EPCHandler
   :parts: 1

.. autoclass:: EPCHandler


EPC exceptions
==============

.. inheritance-diagram::
   EPCErrorNoID
   ReturnErrorNoID
   :parts: 1

.. autoclass:: BaseEPCError
.. autoclass:: IDNoFound
.. autoclass:: EPCError
.. autoclass:: ReturnError
.. autoclass:: EPCErrorNoID
.. autoclass:: ReturnErrorNoID


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
