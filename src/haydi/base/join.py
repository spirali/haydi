from .domain import Domain

from random import randint


class Join(Domain):

    def __init__(self, domains, ratios=None, name=None):
        super(Join, self).__init__(name)
        domains = tuple(domains)
        self._set_flags_from_domains(domains)
        self.domains = domains
        self.ratios = ratios
        self.ratio_sums = None

    def _compute_size(self):
        size = 0
        for d in self.domains:
            s = d.size
            if s is None:
                return None
            size += s
        return size

    def create_cn_iter(self):
        for d in self.domains:
            for item in d.create_cn_iter():
                yield item

    def create_iter(self, step=0):
        if not self.domains:
            return

        if step >= self.size:
            return

        index = 0
        while step > self.domains[index].size:
            step -= self.domains[index].size
            index += 1

        while index < len(self.domains):
            it = self.domains[index].create_iter(step)
            step = 0
            for v in it:
                yield v
            index += 1

    def _compute_ratio_sums(self):
        ratios = self.ratios
        if ratios is None:
            ratios = (d.size if d.size is not None else 1
                      for d in self.domains)
        ratio_sums = []
        s = 0
        for r in ratios:
            s += r
            ratio_sums.append(s)
        self.ratio_sums = ratio_sums

    def generate_one(self):
        ratio_sums = self.ratio_sums
        if ratio_sums is None:
            self._compute_ratio_sums()
            ratio_sums = self.ratio_sums
        c = randint(0, self.ratio_sums[-1] - 1)
        for i, r in enumerate(self.ratio_sums):
            if c < r:
                return self.domains[i].generate_one()
        assert 0

    def _remap_domains(self, transformation):
        return Join((transformation(d) for d in self.domains),
                    self.ratios, self.name)

    def __add__(self, other):
        return Join(self.domains + (other,))
