import sys

graphs = []
parsing = False
for line in sys.stdin:
    if parsing:
        line = line.strip()
        vertices = line.split()
        graph = []
        for i in xrange(0, len(vertices), 2):
            graph.append((int(vertices[i]), int(vertices[i + 1])))
        graphs.append(graph)

    parsing = not parsing
