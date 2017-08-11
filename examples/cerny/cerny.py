
# This programs goes over finite state automata of a given
# size and verifies Cerny conjuncture

import haydi as hd
from haydi.ext.xenv import ExperimentEnv
from haydi.algorithms import search


def compute(n_states, n_alphabet):

    def check_automaton(delta):

        def step(state, depth):
            for a in alphabet:
                yield frozenset(delta[(s, a)] for s in state)

        delta = delta.to_dict()
        return search.bfs(
            init_state,
            step,
            lambda state, depth: depth if len(state) == 1 else None,
            max_depth=max_steps,
            not_found_value=0)

    states = hd.ASet(n_states, "q")
    alphabet = hd.ASet(n_alphabet, "a")

    delta = hd.Mappings(states * alphabet, states)
    init_state = frozenset(states)

    max_steps = (n_states**3 - n_states) / 6
    pipeline = delta.cnfs().map(check_automaton).max(size=1)
    return pipeline


def main():

    N_SIZE = 5
    A_SIZE = 2

    env = ExperimentEnv("sync",
                        locals(),
                        ["N_SIZE", "A_SIZE"])
    env.parse_args()

    results = env.run(
        compute(N_SIZE, A_SIZE),
        write=True)
    print(results)


if __name__ == "__main__":
    main()
