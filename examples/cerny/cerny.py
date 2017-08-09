
# This programs goes over finite state automata of a given
# size and verifies Cerny conjuncture

import haydi as hd
from haydi.ext.xenv import ExperimentEnv


class SyncDLTS(hd.DLTS):

    def __init__(self, delta, actions):
        hd.DLTS.__init__(self, actions)
        self.delta = delta

    def step(self, state, action):
        delta = self.delta
        return frozenset(delta[(s, action)] for s in state)


def is_singleton(s):
    return len(s[0]) == 1


def compute(n_states, n_alphabet):

    def check_automaton(delta):
        lts = SyncDLTS(delta.to_dict(), alphabet)
        result = lts.bfs(init_state, max_steps, return_depth=True) \
            .first(is_singleton).run()
        if result:
            return delta, result[1]

    states = hd.ASet(n_states, "q")
    alphabet = hd.ASet(n_alphabet, "a")

    delta = hd.Mapping(states * alphabet, states)
    init_state = frozenset(states)

    max_steps = (n_states**3 - n_states) / 6
    pipeline = delta.cnfs().map(check_automaton) \
                           .max(lambda x: x[1] if x else 0, size=1)
    return pipeline


N_SIZE = 5
A_SIZE = 2


def main():
    env = ExperimentEnv("sync",
                        globals(),
                        ["N_SIZE", "A_SIZE"])
    env.parse_args()

    results = env.run(
        compute(N_SIZE, A_SIZE),
        write=True)
    print(results)


if __name__ == "__main__":
    main()
