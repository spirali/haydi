"""
Displays graph with job bandwidth and size.
"""

import json
import sys
import matplotlib.pyplot as plt


def plot_bandwidth(jobs):
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.bar(
        [job["index"] for job in jobs],
        [job["size"] / job["duration"] for job in jobs]
    )

    ax.set_ylabel("Instances/sec")
    ax.set_xlabel("Instance id")
    ax.set_title("Job bandwidth")


def plot_size(jobs):
    sizes = sorted(list(set([job["size"] for job in jobs])))
    durations = []
    for size in sizes:
        dur = [job["duration"] for job in jobs if job["size"] == size]
        durations.append(sum(dur) / len(dur))

    fig, ax = plt.subplots(figsize=(20, 10))
    rects = ax.bar(
        sizes,
        durations
    )

    ax.set_ylabel("Average duration")
    ax.set_xlabel("Job size")
    ax.set_title("Job size and duration")

    for index, rect in enumerate(rects):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2.0, height * 1.05,
                str(sizes[index]), ha="center", va="bottom")


def load_jobs(path):
    with open(path, "r") as f:
        return json.load(f)


def print_help():
    print("Usage: python computation_chart.py path_to_job_dump")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        exit(0)

    jobs = load_jobs(sys.argv[1])
    plot_bandwidth(jobs)
    plot_size(jobs)

    plt.show()
