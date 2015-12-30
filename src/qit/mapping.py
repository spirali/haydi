
from domain import Domain, DomainIterator

class Mapping(Domain):

    def __init__(self, key_domain, value_domain):
        self.key_domain = key_domain
        self.value_domain = value_domain

    """
    def iterate(self):
        return MappingIterator(self)
    """

    def generate_one(self):
        result = {}
        value_domain = self.value_domain
        for key in self.key_domain:
            result[key] = value_domain.generate_one()
        return result
