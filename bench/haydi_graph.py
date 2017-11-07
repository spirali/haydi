import sys
import timeit

import haydi as hd


def haydi_parallel_iterate(count):
    nodes = hd.ASet(count, "n")
    graphs = hd.Subsets(hd.Subsets(nodes, 2))
    ctx = hd.DistributedContext(spawn_workers=8)
    return list(graphs.iterate().run(ctx=ctx))


def haydi_cnfs(count):
    nodes = hd.ASet(count, "n")
    graphs = hd.Subsets(hd.Subsets(nodes, 2))
    return list(graphs.cnfs())


count = int(sys.argv[1])

print("Haydi parallel iteration: {}".format(
    timeit.timeit('haydi_parallel_iterate(count)',
                  setup="from __main__ import haydi_parallel_iterate; count="
                        + str(count), number=1)))
print("Haydi cnfs: {}".format(
    timeit.timeit('haydi_cnfs(count)',
                  setup="from __main__ import haydi_cnfs; count="
                        + str(count), number=1)))
