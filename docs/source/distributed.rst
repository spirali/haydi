
Running in a distributed environment
====================================
.. testsetup:: *
   import qit

Haydi can speed up computation by using a cluster of workers to iterate through
a domain in parallel. For that you have to create a
`distributed context <api-context.html>`_ and assign it to a global
``session`` object that keeps track of which parallel context is
currently active.

>>> from qit import session, DistributedContext
>>> # create a cluster with 4 workers
>>> dctx = DistributedContext(spawn_workers=4)
>>> session.set_parallel_context(dctx)

When the context is created and stored in the session, all you have to do is
pass ``True`` to the ``run`` method of a domain.

>>> r = qit.Range(12)
>>> # this will be executed in parallel on 4 workers
>>> r.map(lambda x: x + 1).collect().run(True)
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
