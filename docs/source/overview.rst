
Overview
========

Haydi (Haystack diver) is a **framework for generating discrete structures**. It
provides a way to define a structure from basic building blocks (e.g. Cartesian
product, mappings) and then enumerate all elements, all non-isomorphic elements,
or generate random elements.

* Pure Python implementation (Python 2.7+, PyPy supported)
* MIT license
* Sequential or distributed computation (via `dask/distributed`_)

.. _`dask/distributed`: https://github.com/dask/distributed


Example of usage
----------------

* Let us define **directed graphs on two vertices** (represented as a set of
  edges)::

    >>> import haydi as hd
    >>> nodes = hd.ASet(2, "n")  # A two-element set with (anonymous) elements {n0, n1}
    >>> graphs = hd.Subsets(nodes * nodes)  # Subsets of a cartesian product

* Now we can **iterate all elements**::

    >>> list(graphs.iterate())
    [{}, {(n0, n0)}, {(n0, n0), (n0, n1)}, {(n0, n0), (n0, n1), (n1, n0)}, {(n0,
    # ... 3 lines removed ...
    n1)}, {(n1, n0)}, {(n1, n0), (n1, n1)}, {(n1, n1)}]

* or **iterate all non-isomorphic ones**::

    >>> list(graphs.cnfs())  # cnfs = canonical forms
    [{}, {(n0, n0)}, {(n0, n0), (n1, n1)}, {(n0, n0), (n0, n1)}, {(n0, n0), (n0,
    n1), (n1, n1)}, {(n0, n0), (n0, n1), (n1, n0)}, {(n0, n0), (n0, n1), (n1, n0),
    (n1, n1)}, {(n0, n0), (n1, n0)}, {(n0, n1)}, {(n0, n1), (n1, n0)}]

* or **generate random instances**::

    >>> list(graphs.generate(3))
    [{(n1, n0)}, {(n1, n1), (n0, n0)}, {(n0, n1), (n1, n0)}]


* Haydi supports standard operations like **map, filter and reduce**::

    >>> op = graphs.map(lambda g: len(g)).reduce(lambda x, y: x + y)
    # Just a demonstration pipeline; nothing usefull
    >>> op.run()  

* We can run it transparently as a **distributed application**::

    >>> from haydi import DistributedContext
    # We are now assuming that dask/distributed is running at hostname:1234
    >>> context = DistributedContext("hostname", 1234)
    >>> op.run(ctx=context)
