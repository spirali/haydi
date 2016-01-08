class GraphNode(object):
    def __init__(self, child, data, height):
        self.child = child
        self.data = data
        self.height = height


class IteratorGraph(object):
    def __init__(self, iterator):
        self.origin_iterator = iterator
        self.graph = self._construct(iterator)

    def __iter__(self):
        return IteratorGraph(self.origin_iterator)

    def next(self):
        if self.graph is None:
            raise StopIteration()
        else:
            node = self.graph
            self.graph = node.child
            return node

    def _construct(self, iterator):
        height = 0
        current_level = [iterator]
        next_level = []
        root = None

        while True:
            for it in current_level:
                next_level += it.get_parents()

            root = GraphNode(root, current_level, height)
            height += 1

            if len(next_level) < 1:
                break
            else:
                current_level = next_level
                next_level = []

        return root
