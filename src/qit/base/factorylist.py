class FactoryList(object):
    def __init__(self, iterator_factory):
        self.factory = iterator_factory.copy()
        self.nodes = []

        self.nodes.append(self.factory)
        for tr in iterator_factory.transformations:
            self.nodes.append(tr.copy())

    @property
    def last_transformation(self):
        return self.nodes[-1]

    @property
    def first_transformation(self):
        return self.nodes[1]

    def has_transformations(self):
        return len(self.factory.transformations) > 0

    def create(self):
        iter = self.factory.klass(*self.factory.args, **self.factory.kwargs)
        parent = iter
        for tr in self.nodes[1:]:
            transformation = tr.create(parent)
            parent = transformation

        return parent

    def copy(self):
        return self.copy_starting_at(self.nodes[-1])

    def copy_starting_at(self, node):
        assert node in self.nodes

        start_index = self.nodes.index(node)
        graph = FactoryList(self.factory)
        graph.nodes = []
        for i, node in enumerate(self.nodes):
            if i > start_index:
                break
            copied = node.copy()
            graph.nodes.append(copied)

        return graph

    def prepend(self, node, transformation_factory):
        assert node in self.nodes
        # make sure we don't go beyond the iterator itself
        assert self.nodes.index(node) > 0

        self.nodes.insert(self.nodes.index(node), transformation_factory)

    def append(self, node, transformation_factory):
        assert node in self.nodes

        self.nodes.insert(self.nodes.index(node) + 1, transformation_factory)

    def skip(self, node):
        assert node in self.nodes
        # make sure we don't skip the iterator itself
        assert self.nodes.index(node) > 0

        self.nodes.remove(node)

    def reparent(self, node, parent):
        assert node in self.nodes
        assert parent in self.nodes

        node_index = self.nodes.index(node)
        parent_index = self.nodes.index(parent)

        assert parent_index < node_index

        self.nodes = self.nodes[:parent_index + 1] + self.nodes[node_index:]

    def replace(self, node, transformation_factory):
        assert node in self.nodes

        self.nodes[self.nodes.index(node)] = transformation_factory

    def get_previous_node(self, node):
        index = self.nodes.index(node)
        if index == 0:
            return None
        else:
            return self.nodes[index - 1]

    def get_next_node(self, node):
        index = self.nodes.index(node)
        if index == len(self.nodes) - 1:
            return None
        else:
            return self.nodes[index + 1]
