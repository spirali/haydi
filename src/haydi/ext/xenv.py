import haydi as hd
import argparse
from datetime import datetime, timedelta

try:
    import cPickle as pickle
except ImportError:
    import pickle


class ExperimentEnv(object):

    """A class for common experiment execution. It handles argument parsing and
    executes a pipeline.
    """

    def __init__(self, name, config_dict, config_names):
        assert all(name in config_dict for name in config_names)
        self.name = name
        self.config_dict = config_dict
        self.config_names = config_names
        self.ctx = None
        self.time = None

    def parse_args(self):

        def timeout_parser(value):
            value = value.split(":")
            if len(value) != 2:
                raise ValueError()
            return timedelta(hours=int(value[0]), minutes=int(value[1]))

        parser = argparse.ArgumentParser(description=self.name)
        parser.add_argument("--local",
                            metavar="PROCESSES",
                            type=int,
                            help="Start local parallel parallel computation")
        parser.add_argument("--scheduler",
                            metavar="IP",
                            type=str,
                            help="IP address of scheduler")
        parser.add_argument("--port",
                            metavar="PORT",
                            type=int,
                            default=9010,
                            help="Port of scheduler")

        parser.add_argument("--time",
                            metavar="HOURS:MINUTES",
                            type=timeout_parser,
                            default=None,
                            help="Computation timeout")

        for name in self.config_names:
            parser.add_argument("--" + name,
                                metavar="INT",
                                type=int,
                                default=self.config_dict[name])

        args = parser.parse_args()

        for name in self.config_names:
            self.config_dict[name] = getattr(args, name)

        ctx = None

        if args.local:
            ctx = hd.DistributedContext(port=args.port,
                                        spawn_workers=args.local)

        if args.scheduler:
            ctx = hd.DistributedContext(port=args.port, ip=args.scheduler)

        if ctx:
            self.ctx = ctx

        self.time = args.time

    def run(self, action, write=False, **kwargs):
        config = {name: self.config_dict[name] for name in self.config_names}
        print "Configuration"
        for name in self.config_names:
            print "\t{}: {}".format(name, config[name])
        print "Time:", self.time

        results = action.run(self.ctx, timeout=self.time, **kwargs)
        if write:
            filename = "{}-{}.data".format(
                self.name, datetime.isoformat(datetime.now()))
            print "Writing results into {}".format(filename)
            with open(filename, "w") as f:
                pickle.dump(config, f)
                pickle.dump(results, f)
        return results
