
Domains
=======

The goal of this section is to introduce basic domains in Haydi.

:class:`haydi.Range` -- Range of integers
-----------------------------------------

:class:`haydi.Range` creates a range of iteger numbers.
The domain has a similar interface as :func:`xrange`.

>>> hd.Range(4)
<Range size=4 {0, 1, 2, 3}>

>>> hd.Range(10, 20)  # From 10 upto 20
<Range size=10 {10, 11, 12, 13, ...}>

>>> hd.Range(4, 15, 3)  # From 4 upto 15, step 3
<Range size=3 {4, 7, 10}>


:class:`haydi.Product` -- Caretesian product
--------------------------------------------

:class:`haydi.Product` makes a cartesian product of domains.
The most basic example is:

>>> a = hd.Range(2)
>>> b = hd.Range(3)
>>> hd.Product((a, b))
<Product size=6 {(0, 0), (1, 0), (0, 1), (1, 1), ...}>

Since cartesian product is often used, the operator ``__mul__``
creates :class:`haydi.Product`. Therefore, we can create the
same product as above just by:

>>> a * b # doctest: +SKIP
<Product size=6 {(0, 0), (1, 0), (0, 1), (1, 1), ...}>

Unordered product
+++++++++++++++++

TODO


:class:`haydi.Join` -- Joining domains
--------------------------------------

TODO


:class:`haydi.Values`
---------------------

TODO


:class:`haydi.Sequence`
-----------------------

TODO


:class:`haydi.Mapping`
----------------------

TODO


:class:`haydi.Bool`
-------------------

TODO

