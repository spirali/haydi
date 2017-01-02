from .domain import Domain


class Mapping(Domain):

    def __init__(self, key_domain, value_domain, name=None):
        size = value_domain.size ** key_domain.size
        steps = value_domain.steps ** key_domain.steps
        exact_size = key_domain.exact_size and value_domain.exact_size
        super(Mapping, self).__init__(size, exact_size, steps, name)
        self.key_domain = key_domain
        self.value_domain = value_domain

    def create_iter(self, step=0):
        if step >= self.steps:
            return
        keys = tuple(self.key_domain)
        if not keys:
            return

        if step:
            iters = []
            steps = self.value_domain.steps
            for key in keys:
                iters.append(self.value_domain.create_iter(step % steps))
                step /= steps
        else:
            iters = [self.value_domain.create_iter() for key in keys]

        value = {}
        key0 = keys[0]

        ln = len(keys)
        i = ln - 1
        while i < ln:
            if i == 0:
                for v in iters[0]:
                    value[key0] = v
                    yield value.copy()
                i = 1
                iters[0] = self.value_domain.create_iter()
            else:
                try:
                    value[keys[i]] = next(iters[i])
                    i -= 1
                except StopIteration:
                    iters[i] = self.value_domain.create_iter()
                    i += 1

    def create_step_iter(self, step):
        if self.exact_size:
            return self.create_iter(step)
        else:
            assert 0

    def generate_one(self):
        result = {}
        value_domain = self.value_domain
        for key in self.key_domain:
            result[key] = value_domain.generate_one()
        return result
