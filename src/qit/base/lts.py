
from iterator import Iterator
from graph import Graph


class LTS(object):

    def __init__(self, actions):
        self.actions = actions
        self.actions_size = actions.size

    def bfs(self,
            init_state,
            max_depth=None,
            return_depth=False,
            max_states=None):
        return BreadthFirstIterator(
            self,
            init_state,
            max_depth,
            return_depth,
            max_states)

    def make_graph(self, init_state, max_depth=None):
        graph = Graph()
        new_nodes = [graph.node(init_state)]
        new_nodes[0].fillcolor = "gray"
        new_nodes[0].label = self.make_label(new_nodes[0].key)
        depth = 0

        while new_nodes and (max_depth is None or depth < max_depth):
            nodes = new_nodes
            new_nodes = []
            depth += 1
            while nodes:
                node = nodes.pop()
                node.label = self.make_label(node.key)
                for i in xrange(self.actions_size):
                    s = self.step(node.key, i)
                    if s is None:
                        continue
                    n, exists = graph.node_check(s)
                    node.add_arc(n, i)
                    if not exists:
                        new_nodes.append(n)
        for node in new_nodes:
            node.label = self.make_label(node.key)
        return graph

    def make_label(self, state):
        return str(state)

    def step(self, state, action):
        raise NotImplementedError()

    def __mul__(self, lts):
        return LTSProduct(self, lts)


class LTSProduct(LTS):

    def __init__(self, lts1, lts2):
        assert lts1.actions_size == lts2.actions_size
        LTS.__init__(self, lts1.actions)
        self.lts1 = lts1
        self.lts2 = lts2

    def step(self, state, action):
        s1 = self.lts1.step(state[0], action)
        s2 = self.lts2.step(state[1], action)
        if s1 is not None and s2 is not None:
            return (s1, s2)

    def make_label(self, state):
        return "{}\\n{}".format(self.lts1.make_label(state[0]),
                                self.lts2.make_label(state[1]))


class BreadthFirstIterator(Iterator):

    def __init__(self,
                 lts,
                 init_state,
                 max_depth,
                 return_depth,
                 max_states):
        self.lts = lts
        self.return_depth = return_depth
        self.depth = 0
        self.max_depth = max_depth
        self.max_states = max_states
        self.nexts = [init_state]
        self.to_report = 1
        self.states = []
        self.found = set(self.nexts)

    def next(self):
        while True:
            if self.to_report:
                i = self.to_report
                self.to_report -= 1
                if self.return_depth:
                    return (self.nexts[-i], self.depth)
                else:
                    return self.nexts[-i]

            if self.states:
                state = self.states.pop()
                to_report = 0
                for a in xrange(self.lts.actions_size):
                    new_state = self.lts.step(state, a)
                    if new_state is None:
                        continue
                    if new_state not in self.found:
                        self.found.add(new_state)
                        self.nexts.append(new_state)
                        to_report += 1
                self.to_report = to_report
                if self.max_states is not None and len(self.states) > self.max_states:
                    raise StopIteration()
                continue

            self.depth += 1
            if self.depth > self.max_depth or not self.nexts:
                raise StopIteration()
            self.states = self.nexts
            self.nexts = []
