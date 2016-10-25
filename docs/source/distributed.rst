
Running in a distributed environment
====================================
.. testsetup:: *
   import qit

Haydi can parallelize computation by using a cluster of workers to iterate
through a domain. First you have to create a :class:`qit.DistributedContext`
and assign it to a global ``session`` object that keeps track of which
parallel context is currently active.

>>> from qit import session, DistributedContext
>>> # create a cluster with 4 workers
>>> dctx = DistributedContext(spawn_workers=4)
>>> session.set_parallel_context(dctx)

When the context is created and stored in the session, all you have to do is
pass ``True`` to a ``run`` method of an iterator that you want to parallelize.

>>> r = qit.Range(1000) # doctest: +SKIP
>>> # this will be executed in parallel on 4 workers
>>> r.map(lambda x: x + 1).collect().run(True) # doctest: +SKIP

You can launch multiple parallel computations in a sequence, but they cannot be
nested. In the example below, the :func:`worker` function will be invoked on
multiple workers at once so you cannot start additional parallel computation
from within it.
You can thus only parallelize the "outer-most" part of the iterator chain.

>>> def worker(x):
>>>    r = qit.Range(x)
>>>    return r.collect().run(True) # invalid! run() must be used
>>>
>>> qit.Range(100).map(worker).run(True)
