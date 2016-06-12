import logging
import sys
sys.path.insert(0, "../../src")

from eqlevel import compute
from qit.base.session import session
from qit.base.runtime.distributedcontext import DistributedContext, \
    DistributedConfig

N_SIZE = 2            # Number of states
S_SIZE = 1            # Number of stack symbols
A_SIZE = 2            # Number of actions (alphabet size)
DEPTH = 2            # Maximal depth of state space
MAX_STATES = 1000  # Max nodes in state space
COUNT = None         # None = iterate all

logging.disable(logging.INFO)

session.set_parallel_context(DistributedContext(
    DistributedConfig(worker_count=4, port=1800, spawn_compute_nodes=False)))

compute(N_SIZE, S_SIZE, A_SIZE, DEPTH, MAX_STATES, COUNT, True)
