class Node(object):
    def __init__(self, inputs, output, iterator):
        self.inputs = inputs
        self.output = output
        self.iterator = iterator


class Graph(object):
    @staticmethod
    def _construct(iterator):
        nodes = []
        queue = [(iterator, None)]  # (iterator, parent node)

        while len(queue) > 0:
            item = queue.pop()

            new_node = Node([], None, item[0])

            if item[1]:  # if this is a parent of a node, register itself as input and set the parent as output
                item[1].inputs.append(new_node)
                new_node.output = item[1]

            for parent in item[0].get_parents():
                queue.append((parent, new_node))

            nodes.append(new_node)

        return nodes

    def __init__(self, iterator):
        self.nodes = Graph._construct(iterator)
        self.origin_node = self.nodes[0]
