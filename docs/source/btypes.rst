
Set and Map
===========

.. currentmodule:: haydi

Domains distributed with Haydi use standard Python types almost in all places
for example: :class:`Range` creates a domain where elements have type
``int``, :class:`Product` and :class:`Sequences` use ``tuple`` as
elements in the resulting domains. The exceptions are :class:`Subsets`
that use :class:`haydi.Set` and :class:`Mappings` with
:class:`haydi.Map`, even though a natural choice would be a standard ``set`` and
``dict``. The reason is a performance optimization during generation (mainly in
generating :doc:`cnfs`).

If you need, both types can be simply converted into the standard ones::

    >>> import haydi as hd
    >>> a = hd.Range(2)

    >>> hd.Subsets(a).map(lambda s: s.to_set())  # Creates standard Python sets
    <MapTransformation size=4 {set([]), set([0]), set([0, 1]), set([1])}>

    >>> hd.Subsets(a).map(lambda s: s.to_frozenset())  # Creates standard Python frozensets
    <MapTransformation size=4 {frozenset([]), frozenset([0]), frozenset([0, , ...}>

    >>> hd.Mappings(a, a).map(lambda m: m.to_dict())  # Creates standard Python dicts
    <MapTransformation size=4 {{0: 0, 1: 0}, {0: 0, 1: 1}, {0: 1, 1: 0}, {0:, ...}>


.. note:: Classes :class:`Set` and :class:`Map` are not designed for frequent
          searching. If you need it, please convert them to set/dict. From this
          reasons they do not intentionally implement methods ``__in__`` and
          ``__getitem__`` to avoid accident usage theses class instead of
          set/dict. For occasional lookup, there are methods contains/get in
          these classes.

          This is still a subject of discussions if we want to introduce
          ``__in__`` and ``__getitem__`` method for these classes.
