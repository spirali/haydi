class Node(object):
    def __init__(self, factory, input=None, output=None):
        self.factory = factory
        self.input = input
        self.output = output

    def copy(self):
        return Node(self.factory.copy())

    def __repr__(self):
        return "Node with {}".format(self.factory)


class Graph(object):
    def __init__(self, iterator_factory):
        self.factory = iterator_factory.copy()
        self.nodes = []

        parent = Node(self.factory)
        self.nodes.append(parent)
        for tr in iterator_factory.transformations:
            node = Node(tr.copy(), parent)
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
        iter = self.factory.klass(*self.factory.args, **self.factory.kwargs)
        parent = iter
        for tr in self.nodes[1:]:
            transformation = tr.factory.create(parent)
            parent = transformation

        return parent

    def copy(self):
        return self.copy_starting_at(self.nodes[-1])

    def copy_starting_at(self, node):
        assert node in self.nodes

        start_index = self.nodes.index(node)
        graph = Graph(self.factory)
        graph.nodes = []
        parent = None
        for i, node in enumerate(self.nodes):
            if i > start_index:
                break
            copied = node.copy()
            copied.input = parent
            if parent:
                parent.output = copied
            graph.nodes.append(copied)
            parent = copied

        return graph

    def prepend(self, node, transformation_factory):
        assert node.input
        assert node in self.nodes

        new_node = Node(transformation_factory, node.input, node)
        node.input.output = new_node
        node.input = new_node

        self.nodes.insert(self.nodes.index(node), new_node)

        return new_node

    def append(self, node, transformation_factory):
        assert node.input
        assert node in self.nodes

        new_node = Node(transformation_factory, node, node.output)
        if node.output:
            node.output.input = new_node
        node.output = new_node

        self.nodes.insert(self.nodes.index(node) + 1, new_node)

        return new_node

    def skip(self, node):
        assert node.input
        assert node in self.nodes

        parent = node.input
        parent.output = node.output
        node.output = parent
        self.nodes.remove(node)

    def replace(self, node, transformation_factory):
        assert node.input
        assert node in self.nodes

        new_node = Node(transformation_factory, node.input, node.output)
        node.input.output = new_node

        if node.output:
            node.output.input = new_node
        self.nodes[self.nodes.index(node)] = new_node

        return new_node
