#!/usr/bin/env python

from __future__ import print_function
import os
import subprocess
import time
import socket
import sys
import platform
import multiprocessing

from distributed import Client

PORT = 9010
HTTP_PORT = PORT + 1
CPUS = multiprocessing.cpu_count()

def count_workers(address):
    return sum(Client(address).ncores().values())


def get_nodes():
    with open(os.environ["PBS_NODEFILE"]) as f:
        return [line.strip() for line in f]


def main():
    print("PLATFORM: {}".format(platform.python_implementation()), file=sys.stderr)

    env_args = os.environ["HAYDI_ARGS"].split(" ")
    program = env_args[0]

    # start scheduler
    hostname = socket.gethostname()
    master = "{}:{}".format(hostname, PORT)
    subprocess.Popen([
        "dask-scheduler",
        "--port", str(PORT),
        "--http-port", str(HTTP_PORT)
    ])
    time.sleep(1)

    # start workers
    dirname = os.path.dirname(os.path.abspath(__file__))

    nodes = get_nodes()
    total_worker_count = len(nodes) * CPUS - 1
    for i, node in enumerate(nodes):
        worker_count = CPUS - 1 if i == 0 else CPUS
        worker_args = [
            "ssh", node, "--",
            os.path.join(dirname, "worker-helper.sh"),
            os.environ["PBS_O_WORKDIR"],
            master,
            "--nprocs={}".format(str(worker_count))
        ]

        subprocess.Popen(worker_args, cwd=dirname)

    # wait for workers to connect
    while True:
        worker_count = count_workers(master)
        print("WORKER COUNT: {}".format(worker_count), file=sys.stderr)
        if worker_count == total_worker_count:
            break
        time.sleep(2)

    # start program
    program = os.path.abspath(program)
    args = ["--scheduler", hostname, "--port", str(PORT)]
    args += env_args[1:]
    popen_args = ["time", "-p", "python", program] + args

    subprocess.Popen(popen_args, cwd=os.environ["PBS_O_WORKDIR"]).wait()


if __name__ == "__main__":
    main()
