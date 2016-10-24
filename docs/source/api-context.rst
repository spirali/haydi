Contexts
========
Context defines how a computation is executed.
The default (serial) context simply iterates over a domain sequentially.
:class:`DistributedContext` can parallelize the computation to provide speedup.

Distributed context
-------------------

.. autoclass:: qit.DistributedContext
