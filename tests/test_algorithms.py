
from haydi.algorithms import search


def test_alg_bfs():

    def collect(x, depth):
        lst.append(x)

    lst = []
    search.bfs(0, lambda s, d: (), collect)
    assert lst == [0]

    lst = []
    search.bfs(0, lambda s, d: (s + 1,), collect, 0)
    assert lst == [0]

    lst = []
    search.bfs(0, lambda s, d: (s + 1,), collect, 3)
    assert [0, 1, 2, 3] == lst

    lst = []
    search.bfs(False, lambda s, d: (not s,), collect, 100)
    assert lst == [False, True]

    def step(s, depth):
        yield (s[0] + 1, s[1])
        yield (s[0] - 1, s[1])
        yield (s[0], s[1] + 1)
        yield (s[0], s[1] - 1)

    lst = []
    search.bfs((0, 0), step, collect, 2)
    assert len(lst) == len(set(lst))
    assert set(lst) == set([(0, 1),
                            (0, 0),
                            (0, -1),
                            (0, -2),
                            (0, 2),
                            (-1, 1),
                            (-1, 0),
                            (-1, -1),
                            (1, 0),
                            (1, -1),
                            (1, 1),
                            (2, 0),
                            (-2, 0)])

    def check(x, depth):
        if x == (4, 2):
            return depth

    result = search.bfs((0, 0), step, check, None)
    assert result == 6
