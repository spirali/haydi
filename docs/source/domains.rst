
Domains
=======

.. currentmodule:: haydi

This section introduces the core structure of *Haydi*: *domains* and basic operations on
them. Advanced domains and canonical forms are covered in a separate section:
:doc:`cnfs`.


Elementary Domains
------------------

One of basic structures in Haydi is :class:`Domain` that represents a generic
collection of arbitrary objects. Elements in the domain can be iterated or
randomly generated.

There are five *elementary domains* shipped with Haydi: :class:`Range` (range of
integers), :class:`Values` (domain of explicitly listed Python objects),
:class:`ASet` (set of atoms), :class:`Boolean` (two-element domain),
and :class:`NoneDomain` (domain containing only one element: ``None``).

Examples::

  >>> import haydi as hd

  >>> hd.Range(4)  # Domain of four integers
  <Range size=4 {0, 1, 2, 3}>

  >>> hd.Values(["Haystack", "diver"])
  <Values size=2 {'Haystack', 'diver'}>

  >>> hd.ASet(3, "a")  # A set of three atoms
  <ASet id=1 size=3 name=a>

  >>> hd.Boolean()
  <Boolean size=2 {False, True}>

  >>> hd.NoneDomain()
  <NoneDomain size=1 {None}>


:class:`ASet` is a little bit special and it is designed for enumerating
non-isomorphic structures. It is covered in :doc:`cnfs`, we will not use it in
this section. For more information about each elementary domain, see their API
documentations.


Composition
-----------

New domains can be created by composing existing ones. There are the following
compositions: *product*, *sequences*, *subsets*, *mappings*, and *join*.


Cartesian product :math:`(A \times B)`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`Product` creates a domain of all ordered tuples, for example::

    >>> import haydi as hd
    >>> a = hd.Range(2)
    >>> b = hd.Values(("a", "b", "c"))
    >>> hd.Product((a, b))
    <Product size=6 {(0, 'a'), (0, 'b'), (0, 'c'), (1, 'a'), ...}>

alternatively, the same thing can be written by using the infix operator ``*``::

    >>> a * b
    <Product size=6 {(0, 'a'), (0, 'b'), (0, 'c'), (1, 'a'), ...}>

The product can be created on more than two domains::

    >>> hd.Product((a, b, hd.Values["x", "y"]))
    <Product size=12{(0, 'a', 'x'), (0, 'a', 'y'), (0, 'b', 'x'), ...}>

    >>> a * b * hd.Values(["x", "y"])
    <Product size=12{(0, 'a', 'x'), (0, 'a', 'y'), (0, 'b', 'x'), ...}>


Sequences :math:`(A^n)`
~~~~~~~~~~~~~~~~~~~~~~~

:class:`Sequences` is a shortcut for a product over the same domain.
Sequences of a given length can be defined as::

     >>> import haydi as hd
     >>> a = hd.Range(2)
     >>> hd.Sequences(a, 3)  # Sequences of length 3
     <Sequences size=8 {(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ...}>

or sequences with a length in a given range::

     >>> hd.Sequences(a, 0, 2)  # Sequences of length 0 to 2
     <Sequences size=7 {(), (0,), (1,), (0, 0), ...}>

Sequence can also be created by the `**` operator on a domain::

      >>> hd.Range(2) ** 3
      <Sequences size=8 {(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), ...>


Subsets :math:`(\mathcal{P}(A))`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`Subsets` domain creates sets of elements of a given domain;
the following example creates the power set::

      >>> import haydi as hd
      >>> hd.Subsets(hd.Range(2))
      <Subsets size=4 {{}, {0}, {0, 1}, {1}}>

When one argument is provided, it is used to limit subsets to a given size::

      >>> hd.Subsets(hd.Range(3), 2)  # Subsets of size 2
      <Subsets size=3 {{0, 1}, {0, 2}, {1, 2}}>

Two arguments limit the subsets to a size in a given range::

      >>> hd.Subsets(hd.Range(3), 0, 1)  # Subsets of size between 0 and 1
      <Subsets size=4 {{}, {0}, {1}, {2}}>

.. note ::

   Type of elements created by :class:`Subsets` is *not* the standard Python
   ``set``, but :class:`haydi.Set`. For more information, see :doc:`btypes`.
   This behavior can be overridden by argument ``set_class``::

     >>> hd.Subsets(hd.Range(2), set_class=frozenset)
     <Subsets size=4 {frozenset([]), frozenset([0]), frozenset([0, 1]), ...}>
 

Mappings :math:`(A \rightarrow B)`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The domain :class:`Mappings` creates all mappings from a domain to another
domain::

     >>> import haydi as hd
     >>> a = hd.Range(2)
     >>> b = hd.Values(["a", "b"])
     >>> hd.Mappings(a, b)
     <Mappings size=4 {{0: 'a'; 1: 'a'}, {0: 'a'; 1: 'b'}, {0:  ... a'}, ...}>


.. note ::

   Type of elements created by :class:`Mappings` is *not* the standard Python
   ``dict``, but :class:`haydi.Map`. For more information, see :doc:`btypes`.
   This behavior can be overridden by argument ``map_class``::

     >>> hd.Mappings(a, b, map_class=dict)
     <Mappings size=4 {{0: 'a', 1: 'a'}, {0: 'a', 1: 'b'}, {0:  ... a'}, ...}>
    

Join :math:`(A \uplus B)`
~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`Join` operation creates a new domain that contains elements of all given
domains (disjoint union)::

  >>> import haydi as hd
  >>> a = hd.Range(2)
  >>> b = hd.Values(["abc", "ikl", "xyz"])
  >>> c = hd.Values([123])

  >>> hd.Join((a, b, c))
  <Join size=6 {0, 1, 'abc', 'ikl', ...}>

The same behavior can be also achieved by `+` operator on domains::

  >>> a + b + c
  <Join size=6 {0, 1, 'abc', 'ikl', ...}>

Note that :class:`Join` does not collapse the same elements in the joined domains::

  >>> a = hd.Range(2)
  >>> b = hd.Range(3)
  >>> a + b
  <Join size=5 {0, 1, 0, 1, 2}>


TODO example & note on probability distributions


Zip
~~~

:class:`Zip` creates a new domain that contains tuples of consecutive elements from the given
domains::

  >>> import haydi as hd
  >>> a = hd.Range(3)
  >>> b = hd.Values(["a", "b", "c"])

  >>> hd.Zip((a, b))
  <Zip size=3 {(0, 'a'), (1, 'b'), (2, 'c')}>


Laziness of domains
-------------------

A domain is generally a lazy object that does not eagerly construct its elements.
Therefore if we use code like this::

    >>> import haydi as hd
    >>> a = hd.Range(1000000)
    >>> a * a * a
    <Product size=1000000000000000000 {(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 0, 3), ...}>

we obtain the result instantly, it just instantiates first few objects for the
repr string. The ways how to instantiate a domain is explained in :doc:`pipeline`.


Transformations
---------------

Another way of creating new domains is applying a transformation on an existing
domain. There are two basic transformations: **map** and **filter**.


Map
~~~

*Map* transformation takes elements of a domain and applies a function to each
element to create a new domain::

     >>> a = hd.Range(4).map(lambda x: x * 10)
     >>> a
     <MapTransformation size=4 {0, 10, 20, 30}>

The resulting object is again a domain. For example we can make a product of
it::

     >>> a * a
     <Product size=16 {(0, 0), (0, 10), (0, 20), (0, 30), ...}>


Filter
~~~~~~

*Filter* transformation creates a new domain by removing some elements from an
existing domain. What elements are removed is configured by providing a function
that is called for each element and should return True/False. When the function
returns True, then the element is put into the new domain.

    >>> hd.Range(10).filter(lambda x: x % 2 == 0 and x > 5)
    <FilterTransformation size=10 filtered>

As we can see, the returned repr string is a different from what we have seen so
far. The flag 'filtered' means that domain contains a filter transformation and
the size argument is not exact but only an upper bound. The reason is that to
obtain a real size we need to apply the filter function to each element (which
would require going through a potentially very large domain).

If we transform the domain into the list, we force the evaluation of the domain
and obtain::

    >>> list(a)
    [6, 8]

Let us show that the 'filtered' flag is propaged during the composition::

    >>> p = a * a
    <Product size=100 filtered>


Names
-----

It is possible to provide a name for a domain as an argument in the domain
constructor. This name serves only for debugging purposes. For example::

    >>> import haydi as hd
    >>> a = hd.Range(10, name="MyRange")
    >>> a
    <MyRange size=10 {0, 1, 2, 3, ...}>
    >>> a.name
    'MyRange'

    >>> a = hd.Range(10)
    >>> hd.Product((a, a), name="MyProduct")
    <MyProduct size=100 {(0, 0), (0, 1), (0, 2), (0, 3), ...}>

