
# Script for verifying Cerny's conjuncture
#
# This programs goes over finite state automata of a given
# size and finds the maximal length of a minimal reset word

import haydi as hd
from haydi.algorithms import search


def main():

    n_states = 4   # Number of states
    n_symbols = 2  # Number of symbols in alphabet

    states = hd.ASet(n_states, "q")  # set of states q0, q1, ..., q_{n_states}
    alphabet = hd.ASet(n_symbols, "a")  # set of symbols a0, ..., a_{a_symbols}

    # Mappings (states * alphabet) -> states
    delta = hd.Mappings(states * alphabet, states)

    # Let us precompute some values that will be repeatedly used
    init_state = frozenset(states)
    max_steps = (n_states**3 - n_states) / 6

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
            step,        # Step
            lambda state, depth: depth if len(state) == 1 else None,
                         # Run until we reach a single state
            max_depth=max_steps,  # Limit depth of search
            not_found_value=0)    # Return 0 when we exceed depth limit

    # Create & run pipeline
    pipeline = delta.cnfs().map(check_automaton).max(size=1)
    result = pipeline.run()

    print ("The maximal length of a minimal reset word for an "
           "automaton with {} states and {} symbols is {}.".
           format(n_states, n_symbols, result[0]))


if __name__ == "__main__":
    main()
