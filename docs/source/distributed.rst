
Distributed computation
=======================

.. currentmodule:: haydi

Haydi can parallelize computation by using a cluster of workers to iterate
through a domain. First you have to create a :class:`DistributedContext`
and pass it to the :func:`haydi.Domain.run` method.

    >>> from haydi import DistributedContext
    >>> dctx = DistributedContext(spawn_workers=4)
    >>> hd.Range(100).map(lambda x: x + 1).collect().run(ctx=dctx)
    [1, 2, 3, 4, ...]

If you want to parallelize the computation on a single computer,
:class:`DistributedContext` can spawn local workers for you.
The example below will create four workers that will operate in
separate processes.

>>> DistributedContext(spawn_workers=4) # spawns 4 local workers # doctest: +SKIP

If you want to distribute the computation amongst multiple computers, you first
have to create a *distributed* cluster. An example of cluster setup can be
found `here <https://distributed.readthedocs.io/en/latest/setup.html>`_.
Once the cluster is created, simply pass the IP adress and port of the
clusters' scheduler to the context. It will then automatically count the
available workers and use them for parallelization.

>>> DistributedContext(ip='192.168.1.1', port=8787) # connects to cluster at 192.168.1.1:8787 # doctest: +SKIP


You can launch multiple parallel computations in a sequence, but they cannot be
nested. In the example below, the :func:`worker` function will be invoked on
multiple workers at once so you cannot start additional parallel computation
from within it.
You can thus only parallelize the "outer-most" part of the iterator chain.

>>> def worker(x):
...     r = hd.Range(x)
...     # invalid! sequential run() must be used
...     return r.collect().run(DistributedContext(spawn_workers=4))
>>>
>>> hd.Range(100).map(worker).run(DistributedContext(spawn_workers=4)) # doctest: +SKIP
