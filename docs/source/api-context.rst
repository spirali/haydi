Contexts
========
Context defines how a computation is executed.
The default (serial) context simply iterates over a domain sequentially.
:class:`haydi.DistributedContext` can parallelize the computation to provide
speed-up.

To use a parallel context, you have to assign it to a global
``session`` object that keeps tracks of the current active parallel context.

Distributed context
-------------------

.. autoclass:: haydi.DistributedContext
