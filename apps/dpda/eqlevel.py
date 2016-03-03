import sys
sys.path.insert(0, "../../src")
import qit
import qit.ext.automata
from pprint import pprint

N_SIZE = 2            # Number of states
S_SIZE = 2            # Number of stack symbols
A_SIZE = 2            # Number of actions (alphabet size)
DEPTH = 20            # Maximal depth of state space
MAX_STATES = 1000000  # Max nodes in state space
COUNT = 10000         # None = iterate all


def compute(n_size, s_size, a_size, depth, max_states, count):

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
    pda_pairs = qit.UnorderedProduct((pda, pda))
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
        source = pda_pairs.iterate()

    results = source.map(compute_eqlevel_of_two_dpda).max_all(lambda x: x[1]).run()

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


class PdaLTS(qit.LTS):

    def __init__(self, pda, actions):
        qit.LTS.__init__(self, actions)
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


if __name__ == "__main__":
    compute(N_SIZE, S_SIZE, A_SIZE, DEPTH, MAX_STATES, COUNT)
