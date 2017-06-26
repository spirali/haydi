
Cookbook
========

Cookbook of Haydi snippets for commonly occurring patterns:

Graphs
------

Directed graphs::

  >>> nodes = hd.ASet(3, "n")
  >>> graphs = hd.Subsets(nodes * nodes)

Undirected graphs::

  >>> nodes = hd.ASet(3, "n")
  >>> graphs = hd.Subsets(Subsets(nodes, 2))


Automata
--------

Deterministic finite automaton with more accepting states::

   >>> SIMPLE TODO

Deterministic one-counter automata::

   >>> SIMPLE TODO

Deterministic push-down automata::

   >>> SIMPLE TODO
