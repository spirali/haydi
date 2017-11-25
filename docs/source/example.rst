
Example: Černy's conjecture
===========================

The following example shows how to use Haydi for verifying Černy's conjecture
on bounded instances. The conjecture states that the length of a minimal reset
word is bounded by :math:`(n-1)^2` where :math:`n` is the number of states of
the automaton. The reset word is a word that send all states of the automaton to
a unique state.

The example program find the maximal length of a minimal reset word for automata
of a given size. The full source code is in `examples/cerny/cerny.py` in the
repository.

The following approach is a simple one, just a few lines of code, without any
sophisticated optimization. It takes around two minutes (in PyPy) in the
sequential mode to verify the conjecture for automata with five states. It
probably needs many hours to check automata with six states. The state of the
art result is verifying the conjecture for automata for more than 14 states,
but it needs some clever optimizations that are out of scope of this example.

First, we describe deterministic automata by their transition functions
(mapping from pair of state and symbol to a new state)::

    >>> import haydi as hd
    >>> n_states = 4   # Number of states
    >>> n_symbols = 2  # Number of symbols in alphabet

    >>> states = hd.USet(n_states, "q")  # set of states q0, q1, ..., q_{n_states-1}
    >>> alphabet = hd.USet(n_symbols, "a")  # set of symbols a0, ..., a_{a_symbols-1}

    # All Mappings (states * alphabet) -> states
    >>> delta = hd.Mappings(states * alphabet, states)

Now we can create a pipeline that goes through all non-isomorphic automata
and finds maximum among lengths of their minimal reset word::

    >>> pipeline = delta.cnfs().map(check_automaton).max(size=1)
    >>> result = pipeline.run()

    >>> print ("The maximal length of a minimal reset word for an "
    ...        "automaton with {} states and {} symbols is {}.".
    ...        format(n_states, n_symbols, result[0]))


The function ``check_automaton`` takes an automaton (as a transition function)
and returns the length the minimal reset word or 0 when there is no such word.
It is just a simple breath-first search on the set of states::

    from haydi.algorithms import search

    # Let us precompute some values that will be repeatedly used
    init_state = frozenset(states)
    max_steps = (n_states**3 - n_states) / 6
    # Known result is that we do not need more than (n^3 - n) / 6 steps

    def check_automaton(delta):
          # This function takes automaton as a transition function and
          # returns the minimal length of synchronizing word or 0 if there
          # is no such word

          def step(state, depth):
              # A step in bread-first search; gives a set of states
              # and return a set reachable by one step
              for a in alphabet:
                  yield frozenset(delta[(s, a)] for s in state)

          delta = delta.to_dict()
          return search.bfs(
              init_state,  # Initial state
              step,        # Function that takes a node and returns the followers
              lambda state, depth: depth if len(state) == 1 else None,
                          # Run until we reach a single state
              max_depth=max_steps,  # Limit depth of search
              not_found_value=0)    # Return 0 when we exceed depth limit


