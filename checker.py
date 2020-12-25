in_current = 'in_current'
in_encoding = 'in_encoding'
children = 'children'


def get_neighbors_of_status(*a):
    pass


def plot_encoding_tree(*a):
    pass


def get_parent():
    pass


def drag_green_to_parent(t, blue, pre_reds, update_encoding=False):
    # should consider both leaf and non-leaf cases.
    parent = get_parent(t, blue)
    if parent is None or not t.nodes[blue][in_current]:
        return False
    neighbors_of_parent_in_current = get_neighbors_of_status(t, parent, in_current)
    if len(neighbors_of_parent_in_current) > 1:
        return False
    t.nodes[blue][in_current] = False
    t.nodes[parent][in_current] = True
    plot_encoding_tree(t, title=f"to parent: {blue} -> {parent}, count: {count_conflicts(t)}")
    if not update_encoding:
        return True

    # then decide the encoding.
    neighbors_in_encoding = get_neighbors_of_status(t, blue, in_encoding)
    n = len(neighbors_in_encoding)
    red = -1
    if n == 0:
        # both parent and children are not in the encoding.
        red = pre_reds.pop()
    elif n == 1:
        # must be its parent, or its unique children, it cannot be more than one children
        assert len(t.nodes[blue][children]) <= 1
        red = neighbors_in_encoding[0]
    if red != -1:
        # we can drag from red to blue:
        assert t.nodes[red][in_encoding]
        t.nodes[red][in_encoding] = False
        t.nodes[blue][in_encoding] = True
    return True


def drag_green_from_parent(t, red, update_encoding=False):
    parent = get_parent(t, red)
    if parent is None or not t.nodes[parent][in_current]:
        return False
    neighbors_in_current = get_neighbors_of_status(t, red, in_current)
    # the parent is the only vertex in the independent set.
    assert len(neighbors_in_current) == 1 and neighbors_in_current[0] == parent
    # is this true?
    assert t.nodes[parent][children].index(red) == 0
    # drag vertex
    t.nodes[parent][in_current] = False
    t.nodes[red][in_current] = True
    plot_encoding_tree(t, title=f'from parent: {parent} -> {red}, count: {count_conflicts(t)}')
    if not update_encoding:
        return True

    # then check for encoding.
    neighbors_of_parent_in_encoding = get_neighbors_of_status(t, parent, in_encoding)
    n = len(neighbors_of_parent_in_encoding)
    if n == 1:
        t.nodes[neighbors_of_parent_in_encoding[0]][in_encoding] = False
        t.nodes[parent][in_encoding] = True
    return True

def drag_green_from_other_leaves(t, red, to_borrow, pre_reds, update_encoding=False):
    if t.nodes[red][in_current]:
        return False
    blue = to_borrow.pop(0)
    # first check whether this blue vertex can be dragged to its parent, or whether it has been used.
    while drag_green_to_parent(t, blue, pre_reds, update_encoding) or not t.nodes[blue][in_current]:
        blue = to_borrow.pop(0)
    neighbors_in_current = get_neighbors_of_status(t, red, in_current)
    n = len(neighbors_in_current)
    # both parent and children should not be in the indepenent set. Must can be drag since we have tested the drag from parent.
    assert n == 0
    t.nodes[blue][in_current] = False
    t.nodes[red][in_current] = True
    plot_encoding_tree(t, title=f'from other leaves: {blue} -> {red}, count: {count_conflicts(t)}')
    if not update_encoding:
        return True

    # then check for encoding
    blue_parent = get_parent(t, blue)
    t.nodes[blue][in_encoding] = True
    if blue_parent and t.nodes[blue_parent][in_encoding]:
        # the red is will still be in the encoding
        t.nodes[blue_parent][in_encoding] = False
        pre_reds.append(red)
    return True