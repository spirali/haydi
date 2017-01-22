"""
Displays graph with job bandwidth and size.
"""

import json
import sys
import matplotlib.pyplot as plt


def plot_bandwidth_bar(jobs):
    fig, ax = plt.subplots(figsize=(20, 10))

    min_time = jobs[0]["start"]

    ax.bar(
        [(job["start"] - min_time) for job in jobs],
        [job["size"] / job["duration"] for job in jobs],
        [job["end"] - job["start"] for job in jobs]
    )

    ax.set_ylabel("Instances [s]")
    ax.set_xlabel("Time [s]")
    ax.set_title("Job bandwidth")


def plot_bandwidth_line(jobs):
    fig, ax = plt.subplots(figsize=(20, 10))

    min_time = jobs[0]["start"]

    jobs = sorted(jobs, key=lambda x: x["start"] - min_time)

    ax.plot(
        [(job["start"] - min_time) for job in jobs],
        [job["size"] / job["duration"] for job in jobs]
    )

    ax.set_ylabel("Instances [s]")
    ax.set_xlabel("Time [s]")
    ax.set_title("Job bandwidth")


def plot_size_bar(jobs):
    sizes = sorted(list(set([job["size"] for job in jobs])))
    durations = []
    for size in sizes:
        dur = [job["duration"] for job in jobs if job["size"] == size]
        durations.append(sum(dur) / len(dur))

    durations = [job["duration"] for job in jobs]
    min_time = jobs[0]["start"]

    sizes = [job["size"] for job in jobs]
    min_size, max_size = min(sizes), max(sizes)
    size_scale = float(max_size - min_size)

    index_max = jobs[-1]["start"] - jobs[0]["start"]

    fig, ax = plt.subplots(figsize=(20, 10))
    ax.bar(
        [(job["start"] - min_time) for job in jobs],
        durations,
        [((job["size"] - min_size) / size_scale) * (index_max / 100)
         for job in jobs]
    )

    ax.set_ylabel("Average duration [s]")
    ax.set_xlabel("Time [s]")
    ax.set_title("Job size (width) and duration (height)")


def plot_size_line(jobs):
    min_time = jobs[0]["start"]

    jobs = sorted(jobs, key=lambda x: x["start"] - min_time)

    fig, ax = plt.subplots(figsize=(20, 10))
    ax2 = ax.twinx()

    ax.plot(
        [(job["start"] - min_time) for job in jobs],
        [job["duration"] for job in jobs],
        color="red"
    )
    ax2.plot(
        [(job["start"] - min_time) for job in jobs],
        [job["size"] for job in jobs],
        color="blue"
    )

    ax.set_ylabel("Average duration [s]")
    ax2.set_ylabel("Size")
    ax.set_xlabel("Time [s]")
    ax.set_title("Job size (blue) and duration (red)")


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

    plot_bandwidth_line(jobs)
    plot_size_line(jobs)

    plt.show()
