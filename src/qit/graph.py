class Node(object):
    def __init__(self, factory, input=None, output=None):
        self.factory = factory
        self.input = input
        self.output = output

    def __repr__(self):
        return "Node with {}".format(self.factory)


class Graph(object):
    def __init__(self, iterator_factory):
        self.factory = iterator_factory
        self.nodes = []

        parent = Node(iterator_factory)
        self.nodes.append(parent)
        for tr in iterator_factory.transformations:
            node = Node(tr, parent)
            parent.output = node
            parent = node
            self.nodes.append(node)

    @property
    def last_transformation(self):
        return self.nodes[len(self.nodes) - 1]

    @property
    def first_transformation(self):
        return self.nodes[1]

    def has_transformations(self):
        return len(self.factory.transformations) > 0

    def create(self):
        return self.factory.create()

    def get_factory_from(self, node):
        index = self.nodes.index(node)
        factory = self.factory.copy()
        factory.transformations = factory.transformations[:index]
        return factory

    def prepend(self, node, transformation_factory):
        assert node.input

        new_node = Node(transformation_factory, node.input, node)
        node.input.output = new_node
        node.input = new_node

        indices = self._get_indices(node)

        self.nodes.insert(indices[0], new_node)
        self.factory.transformations.insert(indices[1], transformation_factory)

    def append(self, node, transformation_factory):
        assert node.input

        new_node = Node(transformation_factory, node, node.output)
        if node.output:
            node.output.input = new_node
        node.output = new_node

        indices = self._get_indices(node, 1)

        self.nodes.insert(indices[0], new_node)
        self.factory.transformations.insert(indices[1], transformation_factory)

    def skip(self, node):
        assert node.input

        parent = node.input
        parent.output = node.output
        node.output = parent
        self.nodes.remove(node)
        self.factory.transformations.remove(node.factory)

    def replace(self, node, transformation_factory):
        assert node.input

        new_node = Node(transformation_factory, node.input, node.output)
        node.input.output = new_node

        if node.output:
            node.output.input = new_node

        indices = self._get_indices(node)

        self.nodes[indices[0]] = new_node
        self.factory.transformations[indices[1]] = transformation_factory

    def _get_indices(self, node, add=0):
        index = self.nodes.index(node) + add
        return (index, index - 1)
