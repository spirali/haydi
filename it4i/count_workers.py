import sys

from distributed import Client


def print_help():
    print("Usage: python count_workers.py <scheduler_address>")


def main():
    if len(sys.argv) < 1:
        print_help()
        exit()

    address = sys.argv[1]
    client = Client(address)

    print(sum([value for name, value in client.ncores().items()]))

if __name__ == "__main__":
    main()
