import logging

from dill import dill
import umsgpack as msgpack
from mpi4py import MPI


class MpiMessage(object):
    def __init__(self, data=None, tag=None, source=None):
        self.data = data
        self.tag = tag
        self.source = source

    def __repr__(self):
        return "MPI: {} from {}, containing {}".format(
            MpiTag.get_tag_name(self.tag), self.source, self.data)


class MpiTag(object):
    ANY = MPI.ANY_TAG

    NOTIFICATION_MESSAGE = 100

    ITERATOR_ITEM = 200
    ITERATOR_STOP = 201

    APP_QUIT = 300

    NODE_JOB_REQUEST = 400
    NODE_JOB_OFFER = 401
    CALCULATION_START = 402
    CALCULATION_STOP = 403

    ITERATOR_REGION_START = 1000

    @classmethod
    def get_tag_name(cls, tag):
        for attr in cls.__dict__.iteritems():
            if attr[1] == tag:
                return attr[0]
        return "UNKNOWN_TAG"


class MpiCommunicator(object):
    ANY_TAG = MPI.ANY_TAG
    ANY_SOURCE = MPI.ANY_SOURCE

    PICKLE_DILL = 0
    PICKLE_MSGPACK = 1

    def __init__(self, comm=None):
        if not comm:
            comm = MPI.COMM_WORLD

        self.comm = comm

    @property
    def rank(self):
        return self.comm.Get_rank()

    @property
    def size(self):
        return self.comm.Get_size()

    def send(self, data=None, target=None, tag=None, synchronous=False):
        prefix = MpiCommunicator.PICKLE_MSGPACK

        try:
            data = self._serialize_msgpack(data)
        except msgpack.UnsupportedTypeException:
            data = self._serialize_dill(data)
            prefix = MpiCommunicator.PICKLE_DILL

        self._send_bytes(data, target, tag, prefix, synchronous)

    def recv(self, source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG):
        return self._recv_bytes(source, tag)

    def has_message(self, tag=MPI.ANY_TAG, source=MPI.ANY_SOURCE):
        status = MPI.Status()
        return self.comm.iprobe(source=source,
                                tag=tag,
                                status=status)

    def _send_bytes(self, data, target, tag, prefix, synchronous=False):
        array = bytearray(data)
        array.extend([prefix])

        if synchronous:
            self.comm.Ssend((array, len(array), MPI.BYTE), target, tag=tag)
        else:
            self.comm.Send((array, len(array), MPI.BYTE), target, tag=tag)

    def _recv_bytes(self, source, tag):
        status = MPI.Status()
        self.comm.probe(source=source, tag=tag, status=status)

        buffer = bytearray(status.count)
        self.comm.Recv((buffer, len(buffer), MPI.BYTE),
                       tag=tag, source=source, status=status)

        pickle_byte = buffer[-1]
        buffer = buffer[:-1]

        if pickle_byte == MpiCommunicator.PICKLE_DILL:
            buffer = self._deserialize_dill(buffer)
        elif pickle_byte == MpiCommunicator.PICKLE_MSGPACK:
            buffer = self._deserialize_msgpack(buffer)
        else:
            raise BaseException("Invalid data received")

        logging.debug("{} received message with tag {}".format(
            self.rank, MpiTag.get_tag_name(status.tag)))

        return MpiMessage(buffer, status.tag, status.source)

    def _serialize_msgpack(self, obj):
        return msgpack.dumps(obj)

    def _deserialize_msgpack(self, buffer):
        return msgpack.loads(str(buffer))

    def _serialize_dill(self, obj):
        return dill.dumps(obj)

    def _deserialize_dill(self, buffer):
        return dill.loads(buffer)
