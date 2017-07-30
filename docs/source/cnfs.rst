

Canonical forms
===============

.. currentmodule:: haydi

This section covers a feature that serves to iterate only non-isomorphic
elements in a domain. It is based on iterating over `canonical forms`_ -- one
element for each equivalence class of isomorphism_.

Basic building blocks for the whole machinery are *Atoms* and *ASets*, that
allows to define bijections between elements.

.. _`canonical forms`: https://en.wikipedia.org/wiki/Canonical_form
.. _isomorphism: https://en.wikipedia.org/wiki/Isomorphism


Atoms and ASets
---------------

Domain :class:`ASet` contains a finite number of instances of class
:class:`Atom`. When a new ASet is created a number of atoms and a name have to
be specified. With a new ASet new atoms are created. Each atom remembers its
index number and parent ASet that created it::

    >>> import haydi as hd
    >>> aset = hd.ASet(3, "a")  # Create a new Aset
    >>> aset
    <ASet id=1 size=3 name=a>
    >>> list(aset)               # Atoms in aset
    [a0, a1, a2]
    >>> a0, a1, a2 = list(aset)
    >>> a0.index
    0
    >>> a0.parent                # Each Atom remembers its parent ASet
    <ASet id=1 size=3 name=a>


From the perspective of pipeline methods ``iterate()`` and ``generate()``, ASet
behaves as a kind of fancy :class:`Range` that wraps numbers into special
objects.

The main difference between :class:`Range` and :class:`ASet` arises when we
introduce *isomorphism*. Let us remind that two (discrete) objects are
*isomorphic* if there exits a *bijection* between them that preserves the
structure.

In our case, we are establishing bijection between atoms and two objects are
isomorphic when we can obtain one from another by replacing atoms according to
the bijection.

Let us show some examples that use :func:`haydi.is_isomorphic` which checks
isomorphism::

    >>> a0, a1, a2 = hd.ASet(3, "a")

    >>> hd.is_isomorphic(a0, a1)
    True  # Because there is bijection: a0 -> a1; a1 -> a0; a2 -> a2

    >>> hd.is_isomorphic((a0, a1), a1)
    False  # No mapping between atoms can bring us from a tuple to an atom

    >>> hd.is_isomorphic((a0, a1), (a1, a2))
    True  # Because there is mapping: a0 -> a1; a1 -> a2; a2 -> a0

    >>> hd.is_isomorphic((a0, a0), (a0, a1))
    False  # The explanation below

The bijection between objects in the last case cannot exists. The first tuple
represents a pair of the same object and "renaming" a0 to anything else
preserves this property. The second one represents a pair of two different atoms
(even from the same ASet) and any renaming cannot achieve the property of the
first one (any mapping containing ``a0 -> a0; a1 -> a0`` is not bijective)


Atoms from different ASets
--------------------------

Two atoms from different ASets cannot be renamed to each other; i.e. they are
never isomorphic. It can be seen as each ASet and its atoms have a different
color.

    >>> a0, a1 = hd.ASet(2, "a")
    >>> b0, b1 = hd.ASet(2, "b")

    >>> hd.is_isomorphic(a0, b0)  # doctest: +SKIP
    False  # Map containing a0 -> b0 is not allowed

    >>> hd.is_isomorphic((a0, b1), (a1, b0))  # doctest: +SKIP
    True  # There is bijection: a0 -> a1; a1 -> a0; b0 -> b1; b1 -> b0

The bijection in the second case is correct, since each atom has an image from
its parent ASet.

.. note::

   The name of an ASet serves only for the debugging purpose and has no impact
   on behavior. Creating two ASets with the same name still creates two disjoint
   sets of atoms with their own parents.


Basic objects
-------------

So far, we have seen atoms and tuples of atoms in the examples. However, the
whole machinery around isomorphisms is implemented for objects that we call
*basic objects*; they are inductively defined as follows:

* atoms, integers, strings, True, False, and None are basic objects
* a tuple of basic objects is a basic object
* :class:`haydi.Set` of basic objects is a basic object
* :class:`haydi.Map` where keys and values are basic objects is a basic object

Examples::

   >>> a0, a1, a2 = hd.ASet(3, "a")

   >>> hd.is_isomorphic((a0, 1), (a0, 2))
   False  # Renaming is defined only for atoms, not for other objects

   >>> hd.is_isomorphic((a0, 1), (a1, 1))
   True  # Bijection: a0 -> a1; a1 -> a0; a2 -> a2

   >>> hd.is_isomorphic(hd.Set((a0, a1)), hd.Set((a2, a0)))
   True  # Bijection: a0 -> a0; a1 -> a2; a2 -> a1


Canonical forms
---------------

Since we are interested only in finite (basic) objects, they contain only
finitely many atoms, so there are only finitely many bijections (recall that
ASets are finite). Therefore, each class of equivalence induced by
isomorphism is also finite.

In Haydi, there there is a fixed linear ordering of all basic objects defined by
:func:`haydi.compare`. Since each isomorphic class is finite, hence each class
has the smallest element according this ordering. We call this element as a
*canonical form* of the class.

The pipeline method ``cnfs()`` iterates only through canonical elements in a
domain; therefore, we obtain only one element for each equivalence class.

Let us show some examples::

  >>> aset = hd.ASet(3, "a")
  >>> bset = hd.ASet(3, "b")

  >>> list(aset)  # All elements
  [a0, a1, a2]

  >>> list(aset.cnfs())  # Canonical forms
  [a0]

  >>> list(aset + bset)  # All elements
  [a0, a1, a2, b0, b1, b2]

  >>> list((aset + bset).cnfs())  # Canonical forms
  [a0, b0]

  >>> p = aset * aset
  >>> list(p)  # All elements
  [(a0, a0), (a0, a1), (a0, a2),(a1, a0), (a1, a1),
   (a1, a2), (a2, a0), (a2, a1), (a2, a2)]

  >>> list(p.cnfs())  # Canonical forms
  [(a0, a0), (a0, a1)]


  >>> s = hd.Subsets(aset + bset, 2)
  >>> list(s)  # All elements
  [{a0, a1}, {a0, a2}, {a0, b0}, {a0, b1}, {a0, b2}, {a1, a2}, {a1, b0},
   {a1, b1}, {a1, b2}, {a2, b0}, {a2, b1}, {a2, b2}, {b0, b1}, {b0, b2}, {b1, b2}]

  >>> list(s.cnfs())  # Canonical forms
  [{a0, a1}, {a0, b0}, {b0, b1}]


.. _strict-domains:

Strict domains
--------------

The pipeline method ``cnfs()`` is allowed only for *strict* domains. *Strict
domain* is a domain that contains only basic objects and is closed under
isomorphism (if it contains an element, it contains also all isomorphic ones).
We call it "strict", but it is usually not a problem to fulfill these criteria
in practice.

All elementary domains except :class:`Values` are always strict. (Domain
:class:`CnfValues` is a counter-part of :class:`Values` for canonical forms; see
:ref:`cnf-values`). The strictness of a domain can be checked by reading its
attribute ``strict``::

  >>> hd.Range(10).strict
  True

All basic domain compositions preserve strictness if and only if all their inner
domains are also strict, e.g.::

  >>> domain = hd.Subsets(hd.Range(5) * hd.ASet(2))
  >>> domain.strict
  True

The only places where we have to be more careful are transformations and when we
create a strict domain from explicit elements. These topics are covered in next
two subsections.


Transformations on strict domains
---------------------------------

Generally transformations may break strict-domain invariant. A filter may remove
some elements and left some isomorphic ones. A map may even returns some non-basic
objects. Therefore, a domain created by transformation is non-strict by default.

In most cases, when we want to use ``cnfs()`` while applying a transformation,
we can simply move the transformation into the pipeline, where are no such
restrictions, since in the pipeline we do not create a new domain::

   >>> domain = hd.ASet(3, "a") * hd.Range(4)

   >>> list(domain.cnfs())  # This is Ok
   >>> new_domain = domain.map(lambda x: SomeMyClass(x))

   >>> new_domain.strict
   False

   >>> new_domain.cnfs()  # Throws an error

   >>> domain.cnfs().map(lambda x: SomeMyClass(x))  # This is ok, map is in pipeline

If we really need to create a new strict domain by applying a transformation, it
is now possible only with filter by the following way:

   >>> domain = hd.ASet(3, "a") * hd.Range(4)
   >>> new_domain = domain.filter(lambda x: x[1] != 2, strict=True)
   >>> new_domain.strict
   True
   >>> list(new_domain.cnfs())
   [(a0, 0), (a0, 1), (a0, 3)]

When the filter parameter ``strict`` is set to ``True`` and the original domain
is strict, then the resulting domain is still strict. 

.. warning::

   It is the user's responsibility to assure that strict filter removes all
   isomorphic elements. Fortunately, in practice it is usually the desired
   behavior of filters. However, if the rule of strict filter is broken, the
   behavior of ``cnfs()`` is undefined on such a domain.


.. _cnf-values:

Domain :class:`CnfValues`
-------------------------

Domain :class:`Values` creates a non-strict domain, since we cannot assure that
all invariants are valid. If you want to create a strict domain from explicit
elements, you can use :class:`CnfValues`. The difference is that
:class:`CnfValues` is constructed from canonical elements and it automatically
add necessary objects to the domain to make it strict (all elements isomorphic
elements)::

    >>> aset = hd.ASet(3, "a")
    >>> a0, a1, a2 = aset
    >>> domain = hd.CnfValues((a0, (a0, a1), 123))

    >>> list(domain.cnfs())
    [a0, (a0, a1), 123]

    >>> list(domain.iterate())
    [a0, a1, a2, (a0, a1), (a0, a2), (a1, a0), (a1, a2), (a2, a0), (a2, a1), 123]


Public functions
----------------

This is list of public methods that may be useful
when you are working with canonical forms:


* :finc:`is_canonical` -- returns ``True`` if and only if a given is in canonical form.
* :func:`haydi.expand` -- returns a list of isomorphic objects to a given objects.
* :func:`haydi.compare` -- defines a linear ordering between two objects. The
  exact ordering is left is unspecified, but it is guaranteed that for basic
  objects it stays fixed even between separated executions.
* :sort:`haydi.sort` -- sorts object according `hayd.compare`.
