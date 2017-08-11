
def bfs(initial_state, step_fn, eval_fn, max_depth=None, not_found_value=None):
    """Bread-first search"""

    queue2 = [initial_state]
    states = set(queue2)

    depth = 0

    value = eval_fn(initial_state, depth)
    if value is not None:
        return value

    while queue2 and (max_depth is None or depth < max_depth):
        depth += 1
        queue1 = queue2
        queue2 = []

        for state in queue1:
            for s in step_fn(state, depth):
                if s not in states:
                    value = eval_fn(s, depth)
                    if value is not None:
                        return value
                    states.add(s)
                    queue2.append(s)
    return not_found_value
