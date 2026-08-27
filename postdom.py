"""Post-dominator analysis (Phase 3 support).

A node V is post-dominated by W if every path from V to program exit passes
through W. This is exactly dominance computed on the reversed graph, so the
same iterative fixed-point method used for dominators applies, walking over
successors instead of predecessors.

The functions here work on plain ids and an adjacency map so they can be
reused for either the raw CFG or the ENTRY-augmented graph the control
dependence algorithm needs.
"""

from __future__ import annotations


def post_dominators(nodes: set[int], succ: dict[int, list[int]], exit_node: int) -> dict[int, set[int]]:
    """Return, for each node, the set of nodes that post-dominate it (self included)."""
    all_nodes = set(nodes)
    pdom: dict[int, set[int]] = {n: set(all_nodes) for n in all_nodes}
    pdom[exit_node] = {exit_node}

    changed = True
    while changed:
        changed = False
        for n in all_nodes:
            if n == exit_node:
                continue
            new = set(all_nodes)
            for s in succ.get(n, []):
                new &= pdom[s]
            new = {n} | new
            if new != pdom[n]:
                pdom[n] = new
                changed = True
    return pdom


def immediate_post_dominators(pdom: dict[int, set[int]], exit_node: int) -> dict[int, int | None]:
    """Return the immediate post-dominator (tree parent) of each node.

    The immediate post-dominator of n is the unique m among n's strict
    post-dominators whose own post-dominator set equals that strict set.
    """
    ipdom: dict[int, int | None] = {}
    for n, doms in pdom.items():
        if n == exit_node:
            ipdom[n] = None
            continue
        strict = doms - {n}
        ipdom[n] = None
        for m in strict:
            if pdom[m] == strict:
                ipdom[n] = m
                break
    return ipdom