
from iterator import Iterator


class System(object):

    def __init__(self, init_states):
        self.init_states = init_states

    def compute_next(self, state):
        return None

    def iterate_states(self, depth, return_depth=False):
        return StatesIterator(self, depth, return_depth)


class StatesIterator(Iterator):

    def __init__(self, system, max_depth, return_depth):
        self.system = system
        self.return_depth = return_depth
        self.depth = 0
        self.max_depth = max_depth
        self.nexts = list(system.init_states)
        self.to_report = len(system.init_states)
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
                nexts = self.system.compute_next(state)
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
