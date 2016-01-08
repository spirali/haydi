class Visualizer(object):
    def __init__(self):
        pass

    def get_tags(self):
        raise NotImplementedError()

    def handle_message(self, tag, iterator_id, data):
        raise NotImplementedError()
