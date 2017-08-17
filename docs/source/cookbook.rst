
Cookbook
========

Cookbook of Haydi snippets for commonly occurring patterns:

Graphs
------

Directed graphs (subsets of pair of nodes)::

  >>> nodes = hd.ASet(3, "n")
  >>> graphs = hd.Subsets(nodes * nodes)

Undirected graphs (subsets of two-element sets)::

  >>> nodes = hd.ASet(3, "n")
  >>> graphs = hd.Subsets(Subsets(nodes, 2))

Directed graphs with labeled arcs by "x" or "y"::

  >>> nodes = hd.ASet(3, "n")
  >>> graphs = hd.Subsets(nodes * nodes * hd.Values(("x", "y"))

Undirected graphs with 2 "red" and 3 "blue" vertices::

  >>> nodes = hd.ASet(2, "red") + hd.ASet(3, "blue")
  >>> graphs = hd.Subsets(Subsets(nodes, 2))


Automata
--------

Deterministic finite automaton with more accepting states::

   >>> SIMPLE TODO

Deterministic one-counter automata::

   >>> SIMPLE TODO

Deterministic push-down automata::

   >>> SIMPLE TODO
