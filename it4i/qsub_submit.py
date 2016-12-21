#!/usr/bin/env python

import argparse
import os
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--queue",
                        metavar="QUEUE",
                        default="qexp",
                        type=str,
                        help="qsub queue")
    parser.add_argument("-A", "--project",
                        metavar="PROJET",
                        type=str,
                        help="qsub project")
    parser.add_argument("-w", "--walltime",
                        metavar="WALLTIME",
                        default="01:00:00",
                        type=str,
                        help="qsub walltime")
    parser.add_argument("-N", "--name",
                        metavar="NAME",
                        default="haydi-test",
                        type=str,
                        help="qsub name")
    parser.add_argument("-np", "--nodes",
                        metavar="NODES",
                        default=8,
                        type=int,
                        help="number of worker nodes")
    parser.add_argument("-d", "--workdir",
                        metavar="WORK_DIR",
                        type=str,
                        help="qsub working directory")
    parser.add_argument("program")
    parser.add_argument("program_args",
                        nargs=argparse.REMAINDER,
                        default=[],
                        help="arguments for the launched program")

    args = parser.parse_args()
    if args.workdir:
        args.workdir = os.path.abspath(args.workdir)
    args.program = os.path.abspath(args.program)

    popen_args = [
        "qsub",
        "-q", args.queue,
        "-l", "select={}:ncpus=24,walltime={}".format(args.nodes, args.walltime),
        "-N", args.name
    ]

    if args.project:
        popen_args += ["-A", args.project]

    popen_args += ["-v", "HAYDI_ARGS=\"{}\"".format("{} {}".format(args.program, " ".join(args.program_args)))]

    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "qsub_init.sh")
    popen_args.append(script_path)

    print("Args for qsub: {}".format(" ".join(popen_args)))
    result = subprocess.Popen(popen_args,
                              cwd=args.workdir,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).communicate()
    print(result[0])


if __name__ == "__main__":
    main()
