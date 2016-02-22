from testutils import init
init()

import qit  # noqa


def test_system_no_rules():
    s = qit.System([])
    result = list(s.iterate_states(10))
    assert result == []

    s = qit.System(["a", "b"])
    result = list(s.iterate_states(10))
    assert result == ["a", "b"]


def test_system_basic():
    class MySystem(qit.System):
        def compute_next(self, state):
            result = []
            result.append(state * 10)
            if state % 2 == 1:
                result.append(state + 1)
                result.append(state + 2)
            result.append(-state)
            return result

    s = MySystem((10, 21))

    expected = [(-210, 2),  # 21, f, h
                (-100, 2),  # 10, f, h
                (-23, 2),  # 21, g, h
                (-22, 2),  # 21, g, h
                (-21, 1),  # 21, h
                (-20, 2),  # 20, h, g
                (-19, 2),  # 20, h, g
                (-10, 1),  # 10, h
                (10, 0),  # 10
                (21, 0),  # 21
                (22, 1),  # 21, g
                (23, 1),  # 21, g
                (24, 2),  # 21, g, g
                (25, 2),  # 21, g, g
                (100, 1),  # 10, f
                (210, 1),  # 21, f
                (220, 2),  # 21, g, f
                (230, 2),  # 21, g, f
                (1000, 2),  # 10, f, f
                (2100, 2)]  # 21, f, f

    result = sorted(s.iterate_states(2, return_depth=True))
    assert result == expected

    result = sorted(s.iterate_states(2, return_depth=False))
    assert result == [state for state, depth in expected]
