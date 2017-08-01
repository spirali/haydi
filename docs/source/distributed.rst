
Distributed computation
=======================

.. currentmodule:: haydi

The pipeline computation in Haydi can be transparently executed through
`dask/distributed <https://distributed.readthedocs.io/>`_. This enables
distributed computation or local parallel computation.

Switching pipeline from default serial context to distributed one, is done
through providing a class to ``run`` method in the pipeline.


Local computation
-----------------

The following example shows how to start four local dask/distributed workers and
run Haydi computation on them:


    >>> from haydi import DistributedContext
    >>> dctx = DistributedContext(spawn_workers=4)
    >>> hd.Range(100).map(lambda x: x + 1).collect().run(ctx=dctx)
    [1, 2, 3, 4, ...]

The argument ``spawn_workers`` forces :class:`DistributedContext` to spawn
dask/distributed workers for you. Switching pipeline from default serial context
to distributed one, is done through providing a distributed context to ``run``
method in the pipeline.


Distributed computation
-----------------------

If you want to distribute the computation amongst multiple computers, you first
have to create a *distributed* cluster. An example of cluster setup can be found
`here <https://distributed.readthedocs.io/en/latest/setup.html>`_. Once the
cluster is created, simply pass the IP adress and port of the clusters'
scheduler to the context::

  >>> dctx = DistributedContext(ip='192.168.1.1', port=8787)  # doctest: +SKIP
  # connects to cluster at 192.168.1.1:8787
  >>> hd.Range(100).map(lambda x: x + 1).collect().run(ctx=dctx)
  [1, 2, 3, 4, ...]


Limitations
-----------

The nested distributed computations are not allowed, i.e. you cannot run
distributed pipeline in another distributed pipeline. The following example
shows the invalid case::

  >>> def worker(x):
  ...     r = hd.Range(x)
  ...     # invalid! sequential run() must be used
  ...     return r.collect().run(DistributedContext(spawn_workers=4))
  # THIS IS INVALID - nested distributed computations are not allowed
  >>> hd.Range(100).map(worker).run(DistributedContext(spawn_workers=4)) # doctest: +SKIP
