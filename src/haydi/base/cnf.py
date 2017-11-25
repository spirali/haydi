import itertools
from .basictypes import sort, collect_atoms, compare, replace_atoms, compare2


def uset_permutations_bounded(uset_and_bounds):
    return itertools.product(
        *(tuple(itertools.permutations(uset.all()[:bound], bound))
          for uset, bound in uset_and_bounds))


def uset_permutations_all(uset_and_bounds):
    return itertools.product(
        *(tuple(itertools.permutations(uset.all(), bound))
          for uset, bound in uset_and_bounds))


def apply_permutation(item, perm):
    return replace_atoms(item, perm.get)


def apply_permutation_with_gaps(item, perm):
    return replace_atoms(item, lambda x: perm.get(x, x))


def make_permutations_all(usets_and_bounds):
    permutations = []
    usets = [uset for uset, bound in usets_and_bounds]
    it = uset_permutations_all(usets_and_bounds)
    next(it)  # Remove identity
    for perm in it:
        result = {}
        for i in xrange(len(usets)):
            a = usets[i].all()
            p = perm[i]
            for j in xrange(len(p)):
                result[a[j]] = p[j]
        permutations.append(result)
    return permutations


def make_permutations_bounded(usets_and_bounds):
    permutations = []
    usets = [uset for uset, bound in usets_and_bounds]
    it = uset_permutations_bounded(usets_and_bounds)
    next(it)  # Remove identity
    for perm in it:
        result = {}
        for i in xrange(len(usets)):
            a = usets[i].all()
            p = perm[i]
            for j in xrange(len(p)):
                result[a[j]] = p[j]
        permutations.append(result)
    return permutations


def get_bounds(item, original_bounds=None):
    if original_bounds:
        bound_dict = original_bounds.copy()
    else:
        bound_dict = {}
    for atom in collect_atoms(item):
        m = bound_dict.get(atom.parent)
        index = atom.index + 1
        if m is None:
            bound_dict[atom.parent] = index
        else:
            if m < index:
                bound_dict[atom.parent] = index
    return bound_dict


def remove_gaps(item):
    atoms = list(collect_atoms(item))
    if not atoms:
        return item
    sort(atoms)
    unique(atoms)
    perm = {}

    a1 = atoms[0]
    if a1.index != 0:
        a2 = a1.parent.get(0)
        perm[a1] = a2
        atoms[0] = a2

    for i in xrange(1, len(atoms)):
        a2 = atoms[i]
        a1 = atoms[i - 1]
        if a1.parent != a2.parent:
            if a2.index != 0:
                a3 = a2.parent.get(0)
                perm[a2] = a3
                atoms[i] = a3
            continue

        if a1.index + 1 == a2.index:
            continue
        a3 = a1.parent.get(a1.index + 1)
        perm[a2] = a3
        atoms[i] = a3
    if perm:
        return apply_permutation_with_gaps(item, perm)
    else:
        return item


def canonize(item, use_remove_gaps=True):
    if use_remove_gaps:
        item = remove_gaps(item)
    bound_dict = get_bounds(item)
    perm = {}
    for p in make_permutations_bounded(bound_dict.items()):
        if compare2(item, perm, item, p) > 0:
            perm = p

    if perm:
        return apply_permutation(item, perm)
    else:
        return item


def is_canonical_naive(item):
    """Simple and unoptimized implementation for testing purpose"""
    bound_dict = get_bounds(item)
    for p in make_permutations_all(bound_dict.items()):
        if compare(apply_permutation(item, p), item) < 0:
            return False
    return True


def is_canonical(item):
    # TODO: This is version for internal purpose
    # where we know that there are no gaps in permutations
    # for public version we would need similar operation
    # as in canonize
    bound_dict = get_bounds(item)
    empty = {}
    for p in make_permutations_bounded(bound_dict.items()):
        if compare2(item, empty, item, p) > 0:
            return False
    return True


def create_candidate_permutations(item, bounds):
    item_bounds = get_bounds(item)
    groups = []
    for uset in item_bounds:
        item_bound = item_bounds[uset]
        global_bound = bounds.get(uset, 0)
        bound = min(item_bound + global_bound, uset.size)
        group = []
        groups.append(group)
        for p in itertools.permutations(range(bound), item_bound):
            if all(i in p for i in range(global_bound, max(p))):
                group.append([uset.get(i) for i in p])

    for group_values in itertools.product(*groups):
        result = {}
        for uset, values in zip(item_bounds, group_values):
            for k, v in zip(uset.all(), values):
                result[k] = v
        yield result


def unique(items):
    if not items:
        return
    i = len(items) - 1
    while i > 0:
        if items[i] == items[i - 1]:
            del items[i]
        i -= 1


def create_candidates(item, bounds):
    candidates = [apply_permutation(item, p)
                  for p in create_candidate_permutations(item, bounds)]
    sort(candidates)
    unique(candidates)
    return candidates


def canonical_builder(domain, item, make_fn, extra_bounds):
    bounds = get_bounds(item, extra_bounds)
    for base_item in domain.create_cn_iter():
        for candidate in create_candidates(base_item, bounds):
            result, next_domain, is_final, new_bounds = \
                make_fn(item, candidate)
            if result is None:
                continue
            if is_canonical(result):
                if is_final:
                    yield result
                if next_domain:
                    for result in canonical_builder(
                            next_domain, result, make_fn, new_bounds):
                        yield result


def expand(item, use_remove_gaps=True):
    if use_remove_gaps:
        item = remove_gaps(item)
    items = [apply_permutation(item, p)
             for p in make_permutations_all(get_bounds(item).items())]
    items.append(item)
    sort(items)
    unique(items)
    return items


def is_isomorphic(item1, item2):
    if type(item1) != type(item2):
        return False
    return canonize(item1) == canonize(item2)
