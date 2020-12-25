import pulp


def solve(group1, group2, dists):
    l1, l2 = len(group1), len(group2)
    joint_prob = [[0 for _ in range(l2)] for _ in range(l1)]
    my_lp_problem = pulp.LpProblem("My LP Problem", pulp.LpMinimize)
    for i in range(l1):
        for j in range(l2):
            joint_prob[i][j] = pulp.LpVariable(f'z_{i}_st_{j}_nd', lowBound=0, cat='Continuous')
    # Constraints
    for i in range(l1):
        my_lp_problem += sum([joint_prob[i][j] for j in range(l2)]) == group1[i].prob
    for j in range(l2):
        my_lp_problem += sum([joint_prob[i][j] for i in range(l1)]) == group2[j].prob

    my_lp_problem += sum([joint_prob[i][j]*dists[i][j] for i in range(l1) for j in range(l2)]), "Z"
    my_lp_problem.solve()
    status = pulp.LpStatus[my_lp_problem.status]
    dist = pulp.value(my_lp_problem.objective)
    return status, dist, joint_prob

