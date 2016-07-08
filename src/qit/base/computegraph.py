class ComputeGraph(object):
    def __init__(self, action_factory):
        """
        :type action_factory: qit.base.factory.ActionFactory
        """
        self.action_factory = action_factory.copy()
        self.iterator_factory = self.action_factory.iterator_factory
        self.transformations = [t.copy()
                                for t in self.iterator_factory.transformations]

    @property
    def last_transformation(self):
        """
        :rtype: qit.base.factory.TransformationFactory
        """
        return self.transformations[-1]

    @property
    def first_transformation(self):
        """
        :rtype: qit.base.factory.TransformationFactory
        """
        return self.transformations[0]

    def has_transformations(self):
        """
        :rtype: bool
        """
        return len(self.transformations) > 0

    def create(self):
        iter = self.iterator_factory.klass(
            *self.iterator_factory.args, **self.iterator_factory.kwargs)
        parent = iter
        for tr in self.transformations:
            transformation = tr.create(parent)
            parent = transformation

        return parent

    def copy(self):
        return self.copy_starting_at(self.transformations[-1])

    def copy_starting_at(self, node):
        assert node in self.transformations

        start_index = self.transformations.index(node)
        graph = ComputeGraph(self.action_factory)
        graph.nodes = []
        for i, node in enumerate(self.transformations):
            if i > start_index:
                break
            copied = node.copy()
            graph.nodes.append(copied)

        return graph

    def prepend(self, node, transformation_factory):
        assert node in self.transformations

        index = self.transformations.index(node)
        self.transformations.insert(index, transformation_factory)

    def append(self, node, transformation_factory):
        assert node in self.transformations

        index = self.transformations.index(node)
        self.transformations.insert(index + 1, transformation_factory)

    def skip(self, node):
        assert node in self.transformations

        self.transformations.remove(node)

    def reparent(self, node, parent):
        assert node in self.transformations
        assert parent in self.transformations

        node_index = self.transformations.index(node)
        parent_index = self.transformations.index(parent)

        assert parent_index < node_index

        first_half = self.transformations[:parent_index + 1]
        self.transformations = first_half + self.transformations[node_index:]

    def replace(self, node, transformation_factory):
        assert node in self.transformations

        index = self.transformations.index(node)
        self.transformations[index] = transformation_factory

    def get_previous_node(self, node):
        """
        :type node: qit.base.factory.TransformationFactory
        :rtype: qit.base.factory.TransformationFactory
        """
        index = self.transformations.index(node)
        if index == 0:
            return None
        else:
            return self.transformations[index - 1]

    def get_next_node(self, node):
        """
        :type node: qit.base.factory.TransformationFactory
        :rtype: qit.base.factory.TransformationFactory
        """
        index = self.transformations.index(node)
        if index == len(self.transformations) - 1:
            return None
        else:
            return self.transformations[index + 1]
