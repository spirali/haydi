from haydi.base.runtime.util import TimeoutManager


def iterate_with_timeout(iterator, timeout):
    timeout_mgr = TimeoutManager(timeout)
    for item in iterator:
        yield item
        if timeout_mgr.is_finished():
            return


def generate(domain):
    while True:
        yield domain.generate_one()


def apply_transformations(iterator, transformations):
    for tr in transformations:
        iterator = tr.transform_iter(iterator)
    return iterator


def choose_iterator(domain, method, transformations=None):
    it = None

    if method == "iterate":
        it = domain.create_iter()
    elif method == "generate":
        it = generate(domain)
    elif method == "cnfs":
        it = domain.create_cn_iter()
    else:
        raise Exception("Internal error, invalid method")

    if transformations:
        it = apply_transformations(it, transformations)

    return it
