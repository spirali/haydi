
Domains
=======

The goal of this section is to introduce basic domains in Haydi.

:class:`qit.Range` -- Range of integers
---------------------------------------

:class:`qit.Range` creates a range of iteger numbers.
The domain has a similar interface as :func:`xrange`.

>>> Range(4)
<Range size=4 {0, 1, 2, 3}>

>>> Range(10, 20)  # From 10 upto 20
<Range size=10 {10, 11, 12, 13, ...}>

>>> Range(4, 15, 3)  # From 4 upto 15, step 3
<Range size=3 {4, 7, 10}>


:class:`qit.Product` -- Caretesian product
------------------------------------------

:class:`qit.Product` makes a cartesian product of domains.
The most basic example is:

>>> a = Range(2)
>>> b = Range(3)
>>> Product((a, b))
<Product size=6 {(0, 0), (1, 0), (0, 1), (1, 1), ...}>

Since cartesian product is often used, the operator ``__mul__``
creates :class:`qit.Product`. Therefore, we can create the
same product as above just by:

>>> a * b
<Product size=6 {(0, 0), (1, 0), (0, 1), (1, 1), ...}>

Unordered product
+++++++++++++++++

TODO


:class:`qit.Join` -- Joining domains
------------------------------------

TODO


:class:`qit.Values`
---------------------

TODO


:class:`qit.Sequence`
---------------------

TODO


:class:`qit.Mapping`
--------------------

TODO


:class:`qit.Bool`
-----------------

TODO

