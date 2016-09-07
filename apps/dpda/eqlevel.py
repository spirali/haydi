import sys
sys.path.insert(0, "../../src")
import qit # noqa
import qit.ext.automata # noqa
from pprint import pprint # noqa


N_SIZE = 2            # Number of states
S_SIZE = 2            # Number of stack symbols
A_SIZE = 2            # Number of actions (alphabet size)
DEPTH = 22            # Maximal depth of state space
MAX_STATES = 100000   # Max nodes in state space
COUNT = 2000000       # None = iterate all


def compute(n_size, s_size, a_size, depth, max_states, count, parallel=False):

    states = qit.Range(n_size)
    symbols = qit.Range(s_size)
    actions = qit.Range(a_size)

    stack_change = qit.Join((qit.Sequence(symbols, 0),
                             qit.Sequence(symbols, 1),
                             qit.Sequence(symbols, 2)),
                            ratios=(1, 1, 1))

    lrule = states * symbols * actions
    rrule = states * stack_change
    pda = qit.Mapping(lrule, rrule)

    def is_pda_normed(pda):
        return NormDecomposition(pda, n_size, s_size).is_all_finite()

    normed_pda = pda.filter(is_pda_normed)
    pda_pairs = qit.Product((normed_pda, normed_pda), unordered=True, cache_size=50)
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

    print "n =", n_size, "; s =", s_size, "; a_size =", a_size
    print "depth =", depth, "; max_states =", max_states
    print "count =", count
    print "total =", pda_pairs.size

    if count is not None:
        source = pda_pairs.generate(count)
    else:
        source = pda_pairs

    results = source.map(compute_eqlevel_of_two_dpda).max_all(
        lambda x: x[1]).run(parallel)

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


def min_null(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


class NormDecomposition(object):

    def __init__(self, pda, n_states, n_symbols):
        self.norms = [[None] * n_states for i in xrange(n_states * n_symbols)]
        rules = []
        self.n_states = n_states
        for rule in pda.items():
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


class PdaLTS(qit.DLTS):

    def __init__(self, pda, actions):
        qit.DLTS.__init__(self, actions)
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
    return qit.ext.automata.transition_fn_to_graph(pda1, rule_fn, 0)


def main():
    parallel = None
    if len(sys.argv) == 2:
        if sys.argv[1] != "--help" and sys.argv[1] != "-h":
            count = int(sys.argv[1])
            ctx = qit.DistributedContext(port=9010, spawn_workers=count)
            qit.session.set_parallel_context(ctx)
            parallel = True
    elif len(sys.argv) == 3:
        port = int(sys.argv[2])
        ctx = qit.DistributedContext(ip=sys.argv[1], port=port)
        qit.session.set_parallel_context(ctx)
        parallel = True
    elif len(sys.argv) == 1:
        parallel = False

    if parallel is None:
        print "Usages"
        print "{} # serial version".format(sys.argv[0])
        print "{} <number-of-local-workers>".format(sys.argv[0])
        print "{} <server-ip> <server-port>".format(sys.argv[0])
        return
    compute(N_SIZE, S_SIZE, A_SIZE, DEPTH, MAX_STATES, COUNT, parallel)

if __name__ == "__main__":
    main()
