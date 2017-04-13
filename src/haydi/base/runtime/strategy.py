from haydi import Values
from haydi.base.runtime.iterhelpers import make_iter_by_method
from .worker import worker_step, worker_precomputed, worker_generator


class WorkerStrategy(object):
    def __init__(self):
        self.worker_args = None
        self.worker_args_future = None

    def get_size(self, domain, method, take_count):
        if method == "generate" and take_count:
            return take_count
        else:
            return domain.size

    def start(self, scheduler):
        self.worker_args = self._create_worker_args(scheduler)
        [self.worker_args_future] = scheduler.executor.scatter(
            [self.worker_args], broadcast=True)

    def get_args_for_batch(self, scheduler, start, job_size):
        return (self.worker_args_future, start, job_size)

    def create_futures(self, scheduler, batches):
        return scheduler.executor.map(self._get_worker_fn(), batches)

    def _create_worker_args(self, scheduler):
        timelimit = None
        if scheduler.timeout_mgr:
            timelimit = scheduler.timeout_mgr.end

        return {
            "domain": scheduler.domain,
            "transformations": scheduler.transformations,
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
    def __init__(self, method):
        super(PrecomputeSourceStrategy, self).__init__()
        self.iterator = None
        self.method = method

    def start(self, scheduler):
        super(PrecomputeSourceStrategy, self).start(scheduler)
        self.iterator = make_iter_by_method(scheduler.domain.get_source(),
                                            self.method)

    def get_args_for_batch(self, scheduler, start, job_size):
        values = []
        for i in xrange(job_size):
            values.append(self.iterator.next())

        return (self.worker_args_future,
                Values(values),
                job_size)

    def _create_worker_args(self, scheduler):
        timelimit = None
        if scheduler.timeout_mgr:
            timelimit = scheduler.timeout_mgr.end

        return {
            "transformations": scheduler.transformations,
            "reduce_fn": scheduler.worker_reduce_fn,
            "reduce_init": scheduler.worker_reduce_init,
            "timelimit": timelimit
        }

    def _get_worker_fn(self):
        return worker_precomputed


class GeneratorStrategy(WorkerStrategy):
    def _get_worker_fn(self):
        return worker_generator
