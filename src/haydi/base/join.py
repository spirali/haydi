from .domain import Domain

from random import randint


class Join(Domain):

    def __init__(self, domains, ratios=None, name=None):
        domains = tuple(domains)
        if all(d.size is not None for d in domains):
            size = sum(d.size for d in domains)
        else:
            size = None
        exact_size = all(d.exact_size for d in domains)
        if all(d.steps is not None for d in domains):
            steps = sum(d.steps for d in domains)
        else:
            steps = None
        super(Join, self).__init__(size, exact_size, steps, name)
        self.domains = domains

        if ratios is None:
            ratios = (d.size if d.size is not None else 1
                      for d in domains)

        ratio_sums = []
        s = 0
        for r in ratios:
            s += r
            ratio_sums.append(s)
        self.ratio_sums = ratio_sums

    def create_iter(self, step=0):
        if not self.domains:
            return

        if step >= self.steps:
            return

        index = 0
        while step > self.domains[index].steps:
            step -= self.domains[index].steps
            index += 1

        while index < len(self.domains):
            it = self.domains[index].create_iter(step)
            step = 0
            for v in it:
                yield v
            index += 1

    def generate_one(self):
        c = randint(0, self.ratio_sums[-1] - 1)
        for i, r in enumerate(self.ratio_sums):
            if c < r:
                return self.domains[i].generate_one()
        assert 0

    def __add__(self, other):
        return Join(self.domains + (other,))
