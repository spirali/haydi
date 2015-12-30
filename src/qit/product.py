
from domain import Domain, DomainIterator


class Product(Domain):

    def __init__(self, domains):
        self.domains = tuple(domains)

    def iterate(self):
        return ProductIterator(self)

    def generate_one(self):
        return tuple(d.generate_one() for d in self.domains)

    @property
    def size(self):
        if not self.domains:
            return 0
        result = 1
        for domain in self.domains:
            result *= domain.size
        return result

    def __mul__(self, other):
        return Product(self.domains + (other,))


class ProductIterator(DomainIterator):

    def __init__(self, domain):
        super(ProductIterator, self).__init__(domain)
        self.iterators = [ d.iterate() for d in domain.domains ]
        self.current = None

    def reset(self):
        for it in self.iterators:
            it.reset()
        self.current = None

    def next(self):
        if self.current:
           for i, it in enumerate(self.iterators):
               try:
                   self.current[i] = next(it)
                   return tuple(self.current)
               except StopIteration:
                   it.reset()
                   self.current[i] = next(it)
           raise StopIteration()
        else:
           self.current = [ next(i) for i in self.iterators ]
           return tuple(self.current)
