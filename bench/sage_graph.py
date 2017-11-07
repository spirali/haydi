import sys
import timeit

from sage.all import graphs


def cgraph(count):
    return list(graphs(count))


def nauty(count):
    return list(graphs.nauty_geng(count))


count = int(sys.argv[1])

print("Cgraph: {}".format(
    timeit.timeit('cgraph(count)',
                  setup="from __main__ import cgraph; count="
                        + str(count), number=3)))
print("Geng wrapper: {}".format(
    timeit.timeit('nauty(count)',
                  setup="from __main__ import nauty; count="
                        + str(count), number=3)))
