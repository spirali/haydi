import haydi as hd
import argparse
from datetime import datetime

try:
    import cPickle as pickle
except:
    import pickle


class ExperimentEnv(object):

    def __init__(self, name, config_dict, config_names):
        assert all(name in config_dict for name in config_names)
        self.name = name
        self.config_dict = config_dict
        self.config_names = config_names
        self.parallel = False

    def parse_args(self):
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
            hd.session.set_parallel_context(ctx)
            self.parallel = True

    def run(self, action, write=False, timeout=None):
        config = {name: self.config_dict[name] for name in self.config_names}
        print "Configuration"
        for name in self.config_names:
            print "\t{}: {}".format(name, config[name])

        results = action.run(self.parallel, timeout)
        if write:
            filename = "{}-{}.data".format(
                self.name, datetime.isoformat(datetime.now()))
            print "Writing results into {}".format(filename)
            with open(filename, "w") as f:
                pickle.dump(config, f)
                pickle.dump(results, f)
        return results
