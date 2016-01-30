from qit.exception import TooManySplits
from qit.factory import TransformationFactory
from qit.graph import Node, Graph
from qit.runtime.message import Message, MessageTag
from qit.session import session
from qit.transform import Transformation, SplitTransformation, JoinTransformation


class Context(object):
    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def is_parallel(self):
        return False

    def run(self, iterator_factory):
        session.post_message(Message(MessageTag.CONTEXT_START))
        result = self.get_result(iterator_factory)
        session.post_message(Message(MessageTag.CONTEXT_STOP))

        return result

    def get_result(self, iterator_factory):
        raise NotImplementedError()

    def init(self):
        pass

    def shutdown(self):
        pass


class ParallelContext(Context):
    def is_parallel(self):
        return True

    def is_master(self):
        raise NotImplementedError()

    def transmit_to_master(self, message):
        raise NotImplementedError()

    def preprocess_splits(self, iterator_factory):
        process_count = 4  # TODO

        node = self._find_first_transform(iterator_factory)
        user_splits = self._count_user_splits(iterator_factory)

        if user_splits > 1:
            raise TooManySplits()
        elif user_splits == 0:
            node.prepend(
                TransformationFactory(None, SplitTransformation, process_count))

        master = True

        while True:
            iterator = node.iterator_class
            if iterator.is_split():
                if not master:
                    node.skip()  # ignore splits in worker region
                else:
                    master = False
            else:
                if master and not iterator.is_stateful():  # split here
                    node.prepend(TransformationFactory(
                        None, SplitTransformation, process_count))
                    master = False
                elif not master and iterator.is_stateful():  # join here
                    node.prepend(
                        TransformationFactory(None, JoinTransformation))
                    master = True

            if node.output:
                node = node.output
            else:
                break

        if not master:
            node.append(TransformationFactory(None, JoinTransformation))

        skipped = []

        node = iterator_factory

        while node:  # remove immediate split-joins
            if node.iterator_class.is_join():
                if node.input.iterator_class.is_split():
                    skipped += [node, node.input]
            node = node.input

        for skipped_node in skipped:
            skipped_node.skip()

        node = iterator_factory
        while node.output:
            node = node.output

        return node

    def _count_user_splits(self, iterator_factory):
        splits = 0
        node = iterator_factory

        while node:
            if node.iterator_class.is_split():
                splits += 1
            node = node.input

        return splits

    def _find_first_transform(self, iterator_factory):
        node = iterator_factory

        while node and node.iterator_class.is_transformation():
            node = node.input

        return node.output
