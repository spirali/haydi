

class Atom(object):

    def __init__(self, parent, index):
        assert index >= 0 and index < parent._size
        self.parent = parent
        self.index = index

    def __repr__(self):
        return "{}{}".format(self.parent.name, self.index)


class Set(object):

    def __init__(self, items, _prepared_items=False):
        if _prepared_items:
            self.items = tuple(items)
        else:
            self.items = tuple(sorted(items, cmp=compare))

    def to_set(self):
        return set(self.items)

    def to_frozenset(self):
        return frozenset(self.items)

    def contains(self, value):
        return value in self.items

    def __len__(self):
        return len(self.items)

    def __eq__(self, other):
        if not isinstance(other, Set):
            return False
        return self.items == other.items

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.items)

    def __repr__(self):
        return "{{{}}}".format(", ".join(repr(i) for i in self.items))


class Map(object):

    def __init__(self, items, _prepared_items=False):
        if _prepared_items:
            self.items = tuple(items)
        else:
            self.items = tuple(sorted(items, cmp=compare))

    def get(self, key):
        for k, v in self.items:
            if k == key:
                return v

    def to_dict(self):
        return dict(self.items)

    def __len__(self):
        return len(self.items)

    def __eq__(self, other):
        if not isinstance(other, Map):
            return False
        return self.items == other.items

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.items)

    def __repr__(self):
        r = []
        for k, v in self.items:
            r.append("{}: {}".format(repr(k), repr(v)))
        return "{{{}}}".format("; ".join(r))


stype_table = (Atom, int, str, tuple, Map, Set)


def is_equal(item1, item2):
    return compare(item1, item2) == 0


def compare_sequence(item1, item2):
    l1 = len(item1)
    l2 = len(item2)
    if l1 == l2:
        for i in xrange(l1):
            c = compare(item1[i], item2[i])
            if c != 0:
                return c
        return 0
    else:
        return cmp(l1, l2)


def compare(item1, item2):
    type1 = type(item1)
    type2 = type(item2)

    if type1 != type2:
        try:
            return cmp(stype_table.index(type1), stype_table.index(type2))
        except ValueError:
            raise Exception(
                "Comparison with non-basic types: item1={}, item2={}".format(
                    repr(item1), repr(item2)))

    if type1 == Atom:
        if item1.parent == item2.parent:
            return cmp(item1.index, item2.index)
        else:
            return cmp(item1.parent.aset_id, item2.parent.aset_id)

    if type1 == tuple:
        return compare_sequence(item1, item2)

    if type1 == int or type2 == str:
        return cmp(item1, item2)

    if type1 == Map:
        return compare_sequence(item1.items, item2.items)

    if type1 == Set:
        return compare_sequence(item1.items, item2.items)

    raise Exception("Unknown type " + repr(type1) + " value: " + repr(item1))


def compare2_sequence(item1, perm1, item2, perm2):
    l1 = len(item1)
    l2 = len(item2)
    if l1 == l2:
        for i in xrange(l1):
            c = compare2(item1[i], perm1, item2[i], perm2)
            if c != 0:
                return c
        return 0
    else:
        return cmp(l1, l2)


def compare2(item1, perm1, item2, perm2):
    type1 = type(item1)
    type2 = type(item2)

    if type1 != type2:
        return cmp(stype_table.index(type1), stype_table.index(type2))

    if type1 == Atom:
        item1 = perm1.get(item1, item1)
        item2 = perm2.get(item2, item2)
        if item1.parent == item2.parent:
            return cmp(item1.index, item2.index)
        else:
            return cmp(item1.parent.aset_id, item2.parent.aset_id)

    if type1 == tuple:
        return compare2_sequence(item1, perm1, item2, perm2)

    if type1 == int or type2 == str:
        return cmp(item1, item2)

    if type1 == Map or type1 == Set:
        items1 = list(item1.items)
        if perm1:
            items1.sort(cmp=lambda i1, i2: compare2(i1, perm1, i2, perm1))
        items2 = list(item2.items)
        if perm2:
            items2.sort(cmp=lambda i1, i2: compare2(i1, perm2, i2, perm2))
        return compare2_sequence(items1, perm1, items2, perm2)

    raise Exception("Unknown type " + repr(type1) + " value: " + repr(item1))


def sort(items):
    items.sort(cmp=compare)


def foreach_atom(item, fn):
    if isinstance(item, Atom):
        fn(item)
    elif isinstance(item, int) or isinstance(item, str):
        return
    elif isinstance(item, tuple):
        for i in item:
            foreach_atom(i, fn)
    elif isinstance(item, Map) or isinstance(item, Set):
        for i in item.items:
            foreach_atom(i, fn)
    else:
        raise Exception("Unknown item: {}".format(repr(item)))


def replace_atoms(item, fn):
    if isinstance(item, Atom):
        return fn(item)
    elif isinstance(item, int) or isinstance(item, str):
        return item
    elif isinstance(item, list) or isinstance(item, tuple):
        return tuple(replace_atoms(i, fn) for i in item)
    elif isinstance(item, Map):
        return Map(replace_atoms(i, fn) for i in item.items)
    elif isinstance(item, Set):
        return Set(replace_atoms(i, fn) for i in item.items)
    else:
        raise Exception("Unknown item: {}".format(repr(item)))


def atom_index(atom):
    return atom.index


def replace_atoms_by_indices(item):
    return replace_atoms(item, atom_index)


def collect_atoms(item):
    result = []
    foreach_atom(item, lambda e: result.append(e))
    return result
