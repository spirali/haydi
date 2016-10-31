
First steps
===========

*Haydi* is Python environment for fast experiments with abstract structures. It
supports enumerating and generating structures and running distributed
computation over them.


Domains
-------

One of Haydi's basic structures is :class:`haydi.Domain`. It represents a
generic collection of arbitrary objects. The one of basic collection is
:class:`haydi.Range`, that behaves similarly to :func:`xrange` in Python
standard library.

>>> import haydi as hd
>>> hd.Range(4)
<Range size=4 {0, 1, 2, 3}>

The two basic operations is to iterate a domain or generate a random element
from it.

>>> r = hd.Range(4)
>>> list(r)
[0, 1, 2, 3]
>>> r.generate_one() # doctest: +SKIP
2


Composition
-----------

A new domains may be created by composing existing domains.
A simple example is cartesian product:

>>> r = hd.Range(4)
>>> hd.Product((r, r))
<Product size=16 {(0, 0), (1, 0), (2, 0), (3, 0), ...}>

:class:`haydi.Product` is a domain, hence its elements
may be iterated or generated.

>>> p = hd.Product((hd.Range(2), hd.Range(3)))
>>> list(p)
[(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]
>>> p.generate_one() # doctest: +SKIP
(0, 2)


Transformations
---------------


Actions
-------


Iterators
---------



