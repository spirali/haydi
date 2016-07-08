from context import Context


class SerialContext(Context):
    def compute_action(self, computegraph, action):
        for item in computegraph.iterator_factory.create():
            if not action.handle_item(item):
                break
