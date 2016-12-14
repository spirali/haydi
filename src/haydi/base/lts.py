
from .iterator import Iterator
from .graph import Graph
from .domain import Domain

import sys


class DLTS(object):

    def __init__(self, actions=None):
        self.actions = actions

    def bfs(self,
            init_state,
            max_depth=sys.maxint,
            return_depth=False,
            max_states=sys.maxint):

        def create_iterator():
            return BreadthFirstIterator(self,
                                        init_state,
                                        max_depth,
                                        return_depth,
                                        max_states)
        domain = Domain(None, False)
        domain.create_iterator = create_iterator
        return domain

    def bfs_path(self,
                 init_state,
                 max_depth=sys.maxint,
                 max_states=sys.maxint):
        def create_iterator():
            return BreadthFirstIterator2(self,
                                         init_state,
                                         max_depth,
                                         max_states)
        domain = Domain(None, False)
        domain.create_iterator = create_iterator
        return domain

    def get_enabled_actions(self, state):
        return self.actions

    def make_graph(self, init_state, max_depth=sys.maxint):
        graph = Graph()
        new_nodes = [graph.node(init_state)]
        new_nodes[0].fillcolor = "gray"
        new_nodes[0].label = self.make_label(new_nodes[0].key)
        depth = 0

        while new_nodes and depth < max_depth:
            nodes = new_nodes
            new_nodes = []
            depth += 1
            while nodes:
                node = nodes.pop()
                key = node.key
                node.label = self.make_label(key)
                for a in self.get_enabled_actions(key):
                    s = self.step(key, a)
                    if s is None:
                        continue
                    n, exists = graph.node_check(s)
                    node.add_arc(n, a)
                    if not exists:
                        new_nodes.append(n)
        for node in new_nodes:
            node.label = self.make_label(node.key)
        return graph

    def make_label(self, state):
        return str(state)

    def step(self, state, action):
        raise NotImplementedError()

    def make_path(self, state, actions):
        result = [state]
        for a in actions:
            state = self.step(state, a)
            if state is None:
                return result
            result.append(state)
        return result

    def __mul__(self, other):
        return DLTSProduct((self, other))


class DLTSProduct(DLTS):

    def __init__(self, systems):
        if any(lts.actions is None for lts in systems):
            actions = None
        else:
            it = iter(frozenset(lts.actions) for lts in systems)
            actions = it.next()
            for a in it:
                actions = actions.intersection(a)

        super(DLTSProduct, self).__init__(actions)
        self.systems = systems

    def get_enabled_actions(self, state):
        if self.actions is not None:
            # if all systems have defined actions then all such actions
            # are enabled in every state
            return self.actions

        # when actions are None then compute enabled action over all systems
        result = None
        for s, lts in zip(state, self.systems):
            if result is None:
                result = frozenset(lts.get_enabled_actions(s))
            else:
                result = result.intersection(lts.get_enabled_actions(s))
        return result

    def step(self, state, action):
        result = []
        for s, lts in zip(state, self.systems):
            new_state = lts.step(s, action)
            if new_state is None:
                return None
            result.append(new_state)
        return tuple(result)

    def make_label(self, state):
        return "\\n".join(lts.make_label(state[idx])
                          for idx, lts in enumerate(self.systems))

    def __mul__(self, other):
        return DLTSProduct(self.systems + (other,))


class BreadthFirstIterator(Iterator):

    def __init__(self, lts, init_state, max_depth, return_depth, max_states):
        super(BreadthFirstIterator, self).__init__()
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
                for a in self.lts.get_enabled_actions(state):
                    new_state = self.lts.step(state, a)
                    if new_state is None:
                        continue
                    if new_state not in self.found:
                        self.found.add(new_state)
                        self.nexts.append(new_state)
                        to_report += 1
                self.to_report = to_report
                if len(self.states) > self.max_states:
                    raise StopIteration()
                continue

            self.depth += 1
            if self.depth > self.max_depth or not self.nexts:
                raise StopIteration()
            tmp = self.states
            self.states = self.nexts
            self.nexts = tmp


class BreadthFirstIterator2(Iterator):

    def __init__(self, lts, init_state, max_depth, max_states):
        super(BreadthFirstIterator2, self).__init__()
        self.lts = lts
        self.depth = 0
        self.max_depth = max_depth
        self.max_states = max_states
        self.nexts = [(init_state, ())]
        self.to_report = 1
        self.states = []
        self.found = set(self.nexts)

    def next(self):
        while True:
            if self.to_report:
                i = self.to_report
                self.to_report -= 1
                return self.nexts[-i]

            if self.states:
                state, path = self.states.pop()
                to_report = 0
                for a in self.lts.get_enabled_actions(state):
                    new_state = self.lts.step(state, a)
                    if new_state is None:
                        continue
                    if new_state not in self.found:
                        self.found.add(new_state)
                        self.nexts.append((new_state, path + (a,)))
                        to_report += 1
                self.to_report = to_report
                if len(self.states) > self.max_states:
                    raise StopIteration()
                continue

            self.depth += 1
            if self.depth > self.max_depth or not self.nexts:
                raise StopIteration()

            tmp = self.states
            self.states = self.nexts
            self.nexts = tmp
