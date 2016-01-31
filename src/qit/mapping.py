
from domain import Domain


class Mapping(Domain):

    def __init__(self, key_domain, value_domain):
        super(Mapping, self).__init__()
        self.key_domain = key_domain
        self.value_domain = value_domain
        self.size = self.value_domain.size ** self.key_domain.size

    def iterate(self):
        return MappingIterator(self)

    def generate_one(self):
        result = {}
        value_domain = self.value_domain
        for key in self.key_domain:
            result[key] = value_domain.generate_one()
        return result


class MappingIterator(DomainIterator):

    def __init__(self, domain):
        super(MappingIterator, self).__init__(domain)
        self.keys = list(domain.key_domain)
        self.iterators = [ domain.value_domain.iterate() for key in self.keys ]
        self.current = None

    def reset(self):
        for it in self.iterators:
            it.reset()
        self.current = None

    def next(self):
        if self.current is not None:
           for key, it in zip(self.keys, self.iterators):
               try:
                   self.current[key] = next(it)
                   return self.current.copy()
               except StopIteration:
                   it.reset()
                   self.current[key] = next(it)
           raise StopIteration()
        else:
           self.current = {}
           for key, it in zip(self.keys, self.iterators):
               self.current[key] = next(it)
           return self.current.copy()
