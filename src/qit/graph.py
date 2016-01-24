class Node(object):
    def __init__(self, iterator, inputs=None, output=None):
        if not inputs:
            inputs = []

        self.iterator = iterator
        self.inputs = inputs
        self.output = output

    def set_input(self, node):
        if len(self.inputs) > 0:
            self.inputs[0] = node
        else:
            self.inputs.append(node)


class Graph(object):
    @staticmethod
    def _construct(iterator):
        nodes = []
        queue = [(iterator, None)]  # (iterator, parent node)

        while len(queue) > 0:
            item = queue.pop()

            new_node = Node(item[0])

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

    def insert_before(self, node, inserted_node):
        parent = node.inputs[0]
        parent.output = inserted_node
        inserted_node.set_input(parent)
        inserted_node.output = node
        node.set_input(inserted_node)

        self.nodes.insert(self.nodes.index(parent), inserted_node)

    def insert_after(self, node, inserted_node):
        child = node.output
        node.output = inserted_node
        inserted_node.set_input(node.output)
        inserted_node.output = child

        if child:
            child.set_input(inserted_node)

        self.nodes.insert(self.nodes.index(node), inserted_node)

    def skip(self, node):
        parent = node.inputs[0]
        parent.output = node.output
        node.output.set_input(parent)
        self.nodes.remove(node)
