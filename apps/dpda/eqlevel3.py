import sys
sys.path.insert(0, "../../src")
import haydi as hd  # noqa
import haydi.ext.automata  # noqa
from haydi.ext.xenv import ExperimentEnv  # noqa
from pprint import pprint  # noqa


N_SIZE = 2            # Number of states
S_SIZE = 1            # Number of stack symbols
A_SIZE = 2            # Number of actions (alphabet size)
DEPTH = 22            # Maximal depth of state space
MAX_STATES = 100000   # Max nodes in state space
GENERATE = 1

MIN_LEVEL = 7
MAX_SAMPLES_PER_LEVEL = 300


def compute(n_size, s_size, a_size, depth, max_states, generate):

    actions = hd.ASet(a_size, "a")

    states = hd.ASet(n_size, "q1_")
    symbols = hd.ASet(s_size, "s1_")

    lrule = states * symbols * actions
    rrule = states * hd.Sequence(symbols, 0, 2)
    delta = hd.Mapping(lrule, rrule)
    normed_delta = delta.filter(is_pda_normed)

    def is_pda_normed(delta):
        return NormDecomposition(delta, n_size, s_size).is_all_finite()
    normed_pda = pda.filter(is_pda_normed)
    p1 = hd.base.values.StrictValues(normed_pda.canonicals())

    #states = hd.ASet(n_size, "q2_")
    #symbols = hd.ASet(s_size, "s1_")

    #lrule = states * symbols * actions
    #rrule = states * hd.Sequence(symbols, 0, 2)
    #pda2 = hd.Mapping(lrule, rrule)

    pair = pda1 * pda1
    print pair.size, pda1.size

    count = 0

    print p1.size
    #p2 = hd.base.values.StrictValues(pda2.canonicals())

    pair = p1 * p1

    #for p in pda1.canonicals():
    for p in pair.canonicals():
        #if count % 1000 == 0:
        #    print count
        count += 1

    print count

    sys.exit(1)

    return None

    pda_pairs = hd.Product((normed_pda, normed_pda),
                           unordered=True,
                           cache_size=50)
    init_state = ((0, 0), (0, 0))

    def is_witness_pair(conf_depth_pair):
        c1 = len(conf_depth_pair[0][0])  # Size of first stack
        c2 = len(conf_depth_pair[0][1])  # Size of second stack
        return c1 != c2 and (c1 == 1 or c2 == 1)

    def compute_eqlevel_of_two_dpda(pda_pair):
        pda1 = PdaLTS(pda_pair[0], actions)
        pda2 = PdaLTS(pda_pair[1], actions)
        x = (pda1 * pda2).bfs(init_state, depth, True, max_states=max_states) \
            .filter(is_witness_pair) \
            .map(lambda s: s[1]).first(None, -1).run()
        return (pda_pair, x)

    def save_lts(pda1, pda2, depth, filename):
        pda1 = PdaLTS(pda1, actions)
        pda2 = PdaLTS(pda2, actions)
        lts = pda1 * pda2
        lts.make_graph(init_state, depth).write(filename)

    if generate:
        source = pda_pairs.generate()
    else:
        source = pda_pairs

    results = source.map(compute_eqlevel_of_two_dpda)
    results = results.filter(lambda x: x[1] >= MIN_LEVEL)
    results = results.groups(lambda x: x[1],
                             MAX_SAMPLES_PER_LEVEL)
    return results

    """
    (p1, p2), value = results[0]
    print "Value {}, Found: {}".format(value, len(results))
    save_lts(p1, p2, value, "result-lts.dot")
    pda_to_graph(p1).write("result-pda1.dot")
    pda_to_graph(p2).write("result-pda2.dot")

    if len(results) > 30:
        print "Showing only first 30 results"
        results = results[:30]

    for i, ((p1, p2), value) in enumerate(results):
        print "Pda1"
        pprint(p2)
        print "Pda2:"
        pprint(p1)
        print "-" * 79
    """


def min_null(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


class NormDecomposition(object):

    def __init__(self, pda, states, symbols):
        n_states = states.size
        n_symbols = symbols.size
        self.norms = [[None] * states for i in xrange(n_states * n_symbols)]
        rules = []
        self.n_states = n_states
        for rule in pda.items:
            lrule, rrule = rule
            if rrule[1]:
                rules.append(rule)
            else:
                state, symbol, action = lrule
                self._get_norms(state, symbol)[rrule[0]] = 1

        changed = True
        while changed:
            changed = False
            for (state, symbol, action), rrule in rules:
                norms = self._get_norms(state, symbol)
                changed |= self._merge_norms(
                    norms, self.get_norms_to_states(rrule[0], rrule[1]), 1)

    def _merge_norms(self, current_norms, new_norms, delta):
        changed = False
        for i, (current, new) in enumerate(zip(current_norms, new_norms)):
            if new is None:
                continue
            new += delta
            if current is None or new < current:
                current_norms[i] = new
                changed = True
        return changed

    def is_all_finite(self):
        for n in self.norms:
            if not any(n):
                return False
        return True

    def get_norms(self, state, stack):
        norms = self.get_norms_to_states(state, stack)
        return reduce(min_null, norms, None)

    def get_norms_to_states(self, state, stack):
        norms = self._get_norms(state, stack[-1])
        if len(stack) == 1:
            return norms
        empty_norms = [None] * self.n_states
        for symbol in stack[:-1]:
            current_norms = empty_norms[:]
            for state, norm in enumerate(norms):
                if norm is None:
                    continue
                self._merge_norms(
                    current_norms, self._get_norms(state, symbol), norm)
            norms = current_norms
        return norms

    def _get_norms(self, state, symbol):
        n_states = self.n_states
        index = state + n_states * symbol
        return self.norms[index]


class PdaLTS(hd.DLTS):

    def __init__(self, pda, actions):
        hd.DLTS.__init__(self, actions)
        self.pda = pda

    def step(self, conf, action):
        if len(conf) == 1:
            return None
        state = conf[0]
        top = conf[-1]
        new_state, new_stack = self.pda[(state, top, action)]
        return (new_state,) + conf[1:-1] + new_stack

    def make_label(self, conf):
        return "{}|{}".format(conf[0], ",".join(map(str, conf[1:])))


def pda_to_graph(pda1):
    def rule_fn(lhs, rhs):
        state, symbol, action = lhs
        new_state, new_symbols = rhs
        new_symbols = ",".join(map(str, new_symbols))
        label = "{},{}/{}".format(symbol, action, new_symbols)
        return (state, label, new_state)
    return haydi.ext.automata.transition_fn_to_graph(pda1, rule_fn, 0)


def main():
    env = ExperimentEnv("ndpda",
                        globals(),
                        ["N_SIZE", "S_SIZE", "A_SIZE",
                         "DEPTH", "MAX_STATES", "GENERATE",
                         "MIN_LEVEL", "MAX_SAMPLES_PER_LEVEL"])
    env.parse_args()
    results = env.run(
       compute(N_SIZE, S_SIZE, A_SIZE, DEPTH, MAX_STATES, GENERATE),
       write=True)

    keys = results.keys()
    keys.sort(reverse=True)
    for key in keys:
        print "Level {}: {} samples".format(key, len(results[key]))

    if results:
        best = max(results.keys())
        print "Example of level {}:".format(best)
        pprint(results[best][0])
        pda_to_graph(results[best][0][0][0]).write("test.dot")

if __name__ == "__main__":
    main()
