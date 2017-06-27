
Running in a distributed environment
====================================

.. currentmodule:: haydi

Haydi can parallelize computation by using a cluster of workers to iterate
through a domain. First you have to create a :class:`DistributedContext`
and assign it to a global ``session`` object that keeps track of which
parallel context is currently active.

>>> from haydi import session, DistributedContext # doctest: +SKIP
>>> dctx = DistributedContext() # doctest: +SKIP
>>> session.set_parallel_context(dctx) # doctest: +SKIP

When the context is created and stored in the session, all you have to do is
pass ``True`` to a ``run`` method of an iterator that you want to parallelize.

>>> r = hd.Range(1000) # doctest: +SKIP
>>> # this will be executed in parallel
>>> r.map(lambda x: x + 1).collect().run(True) # doctest: +SKIP

If you want to parallelize the computation on a single computer,
:class:`DistributedContext` can spawn local workers for you.
The example below will create four workers that will operate in
separate processes.

>>> # spawns 4 local workers
>>> DistributedContext(spawn_workers=4) # doctest: +SKIP

If you want to distribute the computation amongst multiple computers, you first
have to create a *distributed* cluster. An example of cluster setup can be
found `here <https://distributed.readthedocs.io/en/latest/setup.html>`_.
Once the cluster is created, simply pass the IP adress and port of the
clusters' scheduler to the context. It will then automatically count the
available workers and use them for parallelization.

>>> # connects to cluster at 192.168.1.1:8787
>>> DistributedContext(ip='192.168.1.1', port=8787) # doctest: +SKIP

You can launch multiple parallel computations in a sequence, but they cannot be
nested. In the example below, the :func:`worker` function will be invoked on
multiple workers at once so you cannot start additional parallel computation
from within it.
You can thus only parallelize the "outer-most" part of the iterator chain.

>>> def worker(x):
...     r = hd.Range(x)
...     return r.collect().run(True) # invalid! run() must be used
>>>
>>> hd.Range(100).map(worker).run(True) # doctest: +SKIP
