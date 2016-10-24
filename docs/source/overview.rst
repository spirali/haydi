Overview
========

*Haydi* is Python environment for fast experiments with abstract structures. It
supports enumerating and generating structures and running distributed
computation over them.


Domains
-------

One of Haydi's basic structures is :class:`Domain`. It represents a generic
collection of arbitrary objects. A basic collection is :class:`Range`,
that behaves similarly to :func:`xrange` in Python standard library.

>>> import haydi as hd
>>> hd.Range(4)
<Range size=4 {0, 1, 2, 3}>

The two basic operations is to iterate a domain or generate a random element
from it.

>>> r = hd.Range(4)
>>> list(r)
[0, 1, 2, 3]
>>> r.generate_one()
2


Composition
-----------
