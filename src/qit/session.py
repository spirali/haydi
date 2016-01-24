from enum import Enum

from runtime.mpicontext import MpiContext
from runtime.serialcontext import SerialContext
from runtime.processcontext import ProcessContext
from graph import Graph


class ContextType(Enum):
    Serial = 1
    Process = 2
    MPI = 3


class Session(object):
    PROCESS_MAPPING = {
        ContextType.Serial: SerialContext,
        ContextType.Process: ProcessContext,
        ContextType.MPI: MpiContext
    }

    def __init__(self, context_type=ContextType.Serial, debug=False):
        assert context_type in Session.PROCESS_MAPPING

        self.context_type = context_type
        self.listeners = []
        self.debug = debug

    def create_context(self, iterator):
        ctx = Session.PROCESS_MAPPING[self.context_type]()

        iterator.set_context(ctx)

        ctx.on_message_received(self._broadcast_message)

        return ctx

    def create_graph(self, iterator):
        iterator_graph = Graph(iterator)

        if self.debug:
                self._draw_graph(iterator_graph)

        return iterator_graph

    def add_message_listener(self, listener):
        self.listeners.append(listener)

    def _broadcast_message(self, message):
        for listener in self.listeners:
            listener.handle_message(message)

    def _draw_graph(self, graph):
        import graphviz
        import string

        dot = graphviz.Digraph(graph_attr={"rankdir": "LR"})

        name_index = 0
        node_names = {}

        for node in graph.nodes:
            name = string.ascii_uppercase[name_index]
            name_index += 1
            dot.node(name, label=str(node.iterator))
            node_names[node] = name

        for node in graph.nodes:
            for input in node.inputs:
                dot.edge(node_names[input], node_names[node])

        dot.render("iterator-graph", cleanup=True)
