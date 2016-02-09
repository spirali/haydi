
from iterator import Iterator
from graph import Graph

class LTS(object):

    def bfs(self, init_state, depth, return_depth=False):
        return BreadthFirstIterator(self, init_state, depth, return_depth)

    def make_graph(self, init_state, max_depth=None):
        def set_label(node):
            node.label = self.make_label(node.key)

        graph = Graph()
        new_nodes = [graph.node(init_state)]
        new_nodes[0].fillcolor = "gray"
        set_label(new_nodes[0])
        depth = 0

        while new_nodes and (max_depth is None or depth < max_depth):
            nodes = new_nodes
            new_nodes = []
            depth += 1
            while nodes:
                node = nodes.pop()
                set_label(node)
                for i, s in enumerate(self.step(node.key)):
                    n, exists = graph.node_check(s)
                    node.add_arc(n, i)
                    if not exists:
                        new_nodes.append(n)
        for node in new_nodes:
            set_label(node)
        return graph

    def make_label(self, state):
        return str(state)

    def step(self, state):
        raise NotImplementedError()

    def __mul__(self, lts):
        return LTSProduct(self, lts)


class LTSProduct(LTS):

    def __init__(self, lts1, lts2):
        self.lts1 = lts1
        self.lts2 = lts2

    def step(self, state):
        return tuple(zip(self.lts1.step(state[0]),
                         self.lts2.step(state[1])))

    def make_label(self, state):
        return "{}\\n{}".format(self.lts1.make_label(state[0]),
                                self.lts2.make_label(state[1]))


class BreadthFirstIterator(Iterator):

    def __init__(self, system, init_state, max_depth, return_depth):
        self.system = system
        self.return_depth = return_depth
        self.depth = 0
        self.max_depth = max_depth
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
                nexts = self.system.step(state)
                if not nexts:
                    continue
                to_report = 0
                for n in nexts:
                    if n not in self.found:
                        self.found.add(n)
                        self.nexts.append(n)
                        to_report += 1
                self.to_report = to_report
                continue

            self.depth += 1
            if self.depth > self.max_depth or not self.nexts:
                raise StopIteration()
            self.states = self.nexts
            self.nexts = []
