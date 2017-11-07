import networkx
import sys

graphs = []
for line in sys.stdin:
    graphs.append(networkx.parse_graph6(line.strip()))
