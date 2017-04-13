from .util import TimeoutManager


def iterate_with_timeout(iterator, timeout):
    timeout_mgr = TimeoutManager(timeout)
    for item in iterator:
        yield item
        if timeout_mgr.is_finished():
            return


def generate(domain):
    while True:
        yield domain.generate_one()


def iterate_steps(domain, transformations, start, end):
    from haydi import StepSkip

    i = start
    it = apply_transformations(domain.create_step_iter(start), transformations)
    while i < end:
        v = next(it)
        if isinstance(v, StepSkip):
            i += v.value
        else:
            yield v
            i += 1


def apply_transformations(iterator, transformations):
    for tr in transformations:
        iterator = tr.transform_iter(iterator)
    return iterator


def make_iter_by_method(domain, method):
    if method == "iterate":
        it = domain.create_iter()
    elif method == "generate":
        it = generate(domain)
    elif method == "cnfs":
        it = domain.create_cn_iter()
    else:
        raise Exception("Internal error, invalid method")
    return it
