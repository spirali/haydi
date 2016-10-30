"""
Displays information about a running distributed cluster by reading from its
REST HTTP interface.
"""

import json
import pprint
import urllib2
import sys


def get_info_sync(address, port, path):
    return urllib2.urlopen("{}:{}/{}".format(address, port, path)).read()


def format_data(data):
    data = json.loads(data)
    pprint.pprint(data)


def print_help():
    print("Usage: python cluster_info.py <scheduler> <http-port> <path>")
    print("Possible paths:")
    print("workers, processing, tasks")


def main():
    if len(sys.argv) < 4:
        print_help()
        exit()

    server = sys.argv[1]
    port = sys.argv[2]
    path = sys.argv[3]
    format_data(get_info_sync("http://" + server, port, path + ".json"))


if __name__ == "__main__":
    main()
