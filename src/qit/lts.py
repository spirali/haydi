
from iterator import Iterator


class LTS(object):

    def bfs(self, init_state, depth, return_depth=False):
        return BreadthFirstIterator(self, init_state, depth, return_depth)

    def __mul__(self, lts):
        return LTSProduct(self, lts)


class LTSProduct(LTS):

    def __init__(self, lts1, lts2):
        self.lts1 = lts1
        self.lts2 = lts2

    def step(self, state):
        return tuple(zip(self.lts1.step(state[0]),
                         self.lts2.step(state[1])))


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
