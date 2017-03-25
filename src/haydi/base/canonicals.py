import itertools
from basictypes import sort, collect_atoms, compare, replace_atoms, compare2


def aset_permutations(aset_and_bounds):
    return itertools.product(
        *(tuple(itertools.permutations(aset.all()[:bound], bound))
          for aset, bound in aset_and_bounds))


def apply_permutation(item, perm):
    return replace_atoms(item, perm.get)


def apply_permutation_with_gaps(item, perm):
    return replace_atoms(item, lambda x: perm.get(x, x))


def make_permutations(asets_and_bounds):
    permutations = []
    asets = [aset for aset, bound in asets_and_bounds]
    it = aset_permutations(asets_and_bounds)
    next(it)  # Remove identity
    for perm in it:
        result = {}
        for i in xrange(len(asets)):
            a = asets[i].all()
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


def canonize(item, remove_gaps=True):
    if remove_gaps:
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
            item = apply_permutation_with_gaps(item, perm)
    bound_dict = get_bounds(item)
    perm = {}
    for p in make_permutations(bound_dict.items()):
        if compare2(item, perm, item, p) > 0:
            perm = p

    if perm:
        return apply_permutation(item, perm)
    else:
        return item


def is_canonical_naive(item):
    """Simple and unoptimized implementation for testing purpose"""
    bound_dict = get_bounds(item)
    for p in make_permutations(bound_dict.items()):
        if compare(apply_permutation(item, p), item) < 0:
            return False
    return True


def is_canonical(item):
    bound_dict = get_bounds(item)
    empty = {}
    for p in make_permutations(bound_dict.items()):
        if compare2(item, empty, item, p) > 0:
            return False
    return True


def make_candidate_permutations(asets_and_bounds):
    permutations = []
    asets = [aset for aset, bound in asets_and_bounds]
    for perm in aset_permutations(asets_and_bounds):
        result = {}
        for aset, p in zip(asets, perm):
            for a1, a2 in zip(aset.all(), p):
                result[a1] = a2
        permutations.append(result)
    return permutations


def create_candidate_permutations(item, bounds):
    item_bounds = get_bounds(item)
    groups = []
    for aset in item_bounds:
        item_bound = item_bounds[aset]
        global_bound = bounds.get(aset, 0)
        bound = min(item_bound + global_bound, aset.size)
        group = []
        groups.append(group)
        for p in itertools.permutations(range(bound), item_bound):
            if all(i in p for i in range(global_bound, max(p))):
                group.append([aset.get(i) for i in p])

    for group_values in itertools.product(*groups):
        result = {}
        for aset, values in zip(item_bounds, group_values):
            for k, v in zip(aset.all(), values):
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
            if is_canonical(result):
                if is_final:
                    yield result
                if next_domain:
                    for result in canonical_builder(
                            next_domain, result, make_fn, new_bounds):
                        yield result
