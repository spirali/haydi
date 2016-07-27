import logging
import sys
sys.path.insert(0, "../../src")

from eqlevel import compute
from qit.base.session import session
from qit.base.runtime.distributedcontext import DistributedContext

N_SIZE = 2            # Number of states
S_SIZE = 1            # Number of stack symbols
A_SIZE = 2            # Number of actions (alphabet size)
DEPTH = 10            # Maximal depth of state space
MAX_STATES = 100000  # Max nodes in state space
COUNT = None         # None = iterate all

logging.disable(logging.INFO)

"""if len(sys.argv) < 3:
    print("enter ip, port and worker count")
    exit()

ip = sys.argv[1]
port = int(sys.argv[2])
worker_count = int(sys.argv[3])"""

session.set_parallel_context(DistributedContext(port=9001,
                                                spawn_workers=4))

compute(N_SIZE, S_SIZE, A_SIZE, DEPTH, MAX_STATES, COUNT, True)
