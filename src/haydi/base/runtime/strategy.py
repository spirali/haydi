from haydi import Values
from haydi.base.runtime.iterhelpers import make_iter_by_method
from haydi.base.runtime.util import TimeoutManager
from .worker import worker_step, worker_precomputed, worker_generator


class WorkerStrategy(object):
    def __init__(self, pipeline, timeout=None):
        self.pipeline = pipeline
        self.timeout_mgr = TimeoutManager(timeout) if timeout else None
        self.size = self._compute_size(pipeline)

    def _compute_size(self, pipeline):
        if pipeline.method == "generate" and pipeline.take_count:
            return pipeline.take_count
        else:
            return pipeline.domain.size

    def create_cached_args(self):
        return {
            "domain": self.pipeline.domain,
            "transformations": self.pipeline.transformations,
            "reduce_fn": self.pipeline.action.worker_reduce_fn,
            "reduce_init": self.pipeline.action.worker_reduce_init,
            "timelimit": self._get_timelimit()
        }

    def get_args_for_batch(self, cached_args, start, job_size):
        return (cached_args, start, job_size)

    def create_job(self, batches):
        return (self._get_worker_fn(), batches)

    def _get_worker_fn(self):
        raise NotImplementedError()

    def _get_timelimit(self):
        if self.timeout_mgr:
            return self.timeout_mgr.end
        return None


class StepStrategy(WorkerStrategy):
    def _get_worker_fn(self):
        return worker_step


class PrecomputeStrategy(WorkerStrategy):
    def __init__(self, pipeline, timeout):
        super(PrecomputeStrategy, self).__init__(pipeline, timeout)
        self.iterator = make_iter_by_method(pipeline.domain.get_source(),
                                            pipeline.method)

    def create_cached_args(self):
        return {
            "transformations": self.pipeline.transformations,
            "reduce_fn": self.pipeline.action.worker_reduce_fn,
            "reduce_init": self.pipeline.action.worker_reduce_init,
            "timelimit": self._get_timelimit()
        }

    def get_args_for_batch(self, cached_args, start, job_size):
        values = []
        for i in xrange(job_size):
            values.append(self.iterator.next())

        return (cached_args, Values(values), start, job_size)

    def _get_worker_fn(self):
        return worker_precomputed


class GeneratorStrategy(WorkerStrategy):
    def _get_worker_fn(self):
        return worker_generator
