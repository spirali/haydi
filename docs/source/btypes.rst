
Set and Map
===========

Domains distributed with Haydi uses standard Python types almost in all places
for example: :class:`haydi.Range` creates a domain where elements have type
``int``, :class:`haydi.Product` and :class:`haydi.Sequences` uses ``tuple`` as
elements in the resulting domains. The exceptions are :class:`haydi.Subsets`
that uses :class:`haydi.Set` and :class:`haydi.Mappings` with
:class:`haydi.Map`, even a natural choice would be a standard ``set`` and
``dict``. The reason is a performance optimization during generation (mainly in
generating canonical forms).

If you need, both types can be simply converted into standard ones::

    >>> a = hd.Range(2)

    >>> hd.Subsets(a).map(lambda s: s.to_set())  # Creates standard Python sets
    <MapTransformation size=4 {set([]), set([0]), set([0, 1]), set([1])}>

    >>> hd.Subsets(a).map(lambda s: s.to_frozenset())  # Creates standard Python frozensets
    <MapTransformation size=4 {frozenset([]), frozenset([0]), frozenset([0, , ...}>

    >>> hd.Mappings(a, a).map(lambda m: m.to_dict())  # Creates standard Python dicts
    <MapTransformation size=4 {{0: 0, 1: 0}, {0: 0, 1: 1}, {0: 1, 1: 0}, {0:, ...}>


TODO: Why missing __in__ and __getitem__
