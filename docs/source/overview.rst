
Overview
========

Haydi (Haystack diver) is a framework for generating discrete structures;
primarily developed for automata generating, but designed for usage beyond this
use case.

* Pure Python implementation (Python 2.6+, PyPy supported)
* BSD-2 license
* Sequential or distributed computation (via `dask/distributed`_)

.. _`dask/distributed`: https://github.com/dask/distributed

Example of usage
----------------

* Let us define **directed graphs on two vertices** (represented as a set of
  edges)::

    >>> import haydi as hd
    >>> nodes = hd.ASet(2, "n")  # A two-element set with elements {n0, n1}
    >>> graphs = hd.Subsets(nodes * nodes)  # Subsets of a cartesian product

* Now we can **iterate all elements**::

    >>> list(graphs.iterate())
    [{}, {(n0, n0)}, {(n0, n0), (n0, n1)}, {(n0, n0), (n0, n1), (n1, n0)}, {(n0,
    # ... 3 lines removed ...
    n1)}, {(n1, n0)}, {(n1, n0), (n1, n1)}, {(n1, n1)}]

* or **iterate all non-isomorphic ones**::

    >>> list(graphs.cnfs())  # cnfs = cannonical forms
    [{}, {(n0, n0)}, {(n0, n0), (n1, n1)}, {(n0, n0), (n0, n1)}, {(n0, n0), (n0,
    n1), (n1, n1)}, {(n0, n0), (n0, n1), (n1, n0)}, {(n0, n0), (n0, n1), (n1, n0),
    (n1, n1)}, {(n0, n0), (n1, n0)}, {(n0, n1)}, {(n0, n1), (n1, n0)}]

* or **generate random instances**::

    >>> list(graphs.generate(3))
    [{(n1, n0)}, {(n1, n1), {(n0, n0)}, {(n0, n1), (n1, n0)}]


* Haydi supports standard operations like **map, filter, and reduce**::

    >>> op = graphs.map(lambda g: len(g)).reduce(lambda x, y: x + y, associative=True)
    >>> op.run()

* We can run it transparently as **distributed application**::

    >>> from haydi import DistributedContext, session
    >>> ctx = DistributedContext("hostname", 1234)  # Address of dask/distributed server
    >>> session.set_parallel_context(ctx)
    >>> op.run(parallel=True)

* Visualization::

    >>> TODO
