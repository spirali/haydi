from haydi import Values
from .worker import worker_step, worker_precomputed, worker_generator


class WorkerStrategy(object):
    def __init__(self):
        self.worker_args = None
        self.worker_args_future = None
        self.domain = None

    def get_size(self, domain):
        return domain.size

    def start(self, scheduler):
        self.domain = scheduler.domain
        self.worker_args = self._create_worker_args(scheduler)
        [self.worker_args_future] = scheduler.executor.scatter(
            [self.worker_args], broadcast=True)

    def get_args_for_batch(self, start, job_size):
        return (self.worker_args_future, start, job_size)

    def create_futures(self, scheduler, batches):
        return scheduler.executor.map(self._get_worker_fn(), batches)

    def _create_worker_args(self, scheduler):
        timelimit = None
        if scheduler.timeout_mgr:
            timelimit = scheduler.timeout_mgr.end

        return {
            "domain": scheduler.domain,
            "reduce_fn": scheduler.worker_reduce_fn,
            "reduce_init": scheduler.worker_reduce_init,
            "timelimit": timelimit
        }

    def _get_worker_fn(self):
        raise NotImplementedError()


class StepStrategy(WorkerStrategy):
    def _get_worker_fn(self):
        return worker_step


class PrecomputeSourceStrategy(WorkerStrategy):
    def __init__(self):
        super(PrecomputeSourceStrategy, self).__init__()
        self.iterator = None

    def get_size(self, domain):
        return domain.get_source().size

    def start(self, scheduler):
        super(PrecomputeSourceStrategy, self).start(scheduler)
        self.iterator = scheduler.domain.get_source().create_iter()

    def get_args_for_batch(self, start, job_size):
        values = []
        for i in xrange(job_size):
            values.append(self.iterator.next())

        return (self.worker_args_future, self._set_source(self.domain, values),
                job_size)

    def _create_worker_args(self, scheduler):
        timelimit = None
        if scheduler.timeout_mgr:
            timelimit = scheduler.timeout_mgr.end

        return {
            "reduce_fn": scheduler.worker_reduce_fn,
            "reduce_init": scheduler.worker_reduce_init,
            "timelimit": timelimit
        }

    def _set_source(self, domain, values):
        return domain.set_source(Values(values))

    def _get_worker_fn(self):
        return worker_precomputed


class GeneratorStrategy(WorkerStrategy):
    def _get_worker_fn(self):
        return worker_generator
