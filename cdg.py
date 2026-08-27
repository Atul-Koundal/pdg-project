"""Control dependence graph construction (Phase 3).

This applies the algorithm from Section 3.1.1 of the paper:

  1. Augment the CFG with an ENTRY predicate node that has a True edge to
     START and a False edge to STOP. ENTRY represents the external condition
     that starts the program, so statements that always run come out as
     control dependent on ENTRY.
  2. Build the post-dominator tree of the augmented graph.
  3. For every CFG edge (A, B) where B does not post-dominate A, walk up the
     post-dominator tree from B until reaching A's parent, marking each node
     visited as control dependent on A with that edge's True/False label.

The result is the control dependence subgraph: an edge A -> C labelled T or F
means "C executes exactly when control leaves A along that branch." Control
dependence edges are drawn dashed, following the paper's figures.

Region-node factoring (which would group the several nodes that share the
same control condition, for example everything hanging off ENTRY) is a
refinement noted for a later step and is not performed here.
"""

from __future__ import annotations

from .graph import Graph
from .postdom import immediate_post_dominators, post_dominators

_ENTRY = -1  # synthetic id for the augmented ENTRY node


def control_dependences(cfg: Graph):
    """Return (list of (A, B, label) control dependences, ENTRY id)."""
    # Build the augmented successor map: all CFG edges plus ENTRY -> START/STOP.
    nodes = set(cfg.nodes.keys()) | {_ENTRY}
    succ: dict[int, list[int]] = {nid: [] for nid in cfg.nodes}
    label_of: dict[tuple[int, int], str] = {}
    for (s, d, lbl) in cfg.edges:
        succ[s].append(d)
        label_of[(s, d)] = lbl
    succ[_ENTRY] = [cfg.entry, cfg.exit]
    label_of[(_ENTRY, cfg.entry)] = "T"
    label_of[(_ENTRY, cfg.exit)] = "F"

    pdom = post_dominators(nodes, succ, cfg.exit)
    ipdom = immediate_post_dominators(pdom, cfg.exit)

    all_edges = [(_ENTRY, cfg.entry), (_ENTRY, cfg.exit)]
    all_edges += [(s, d) for (s, d, _l) in cfg.edges]

    seen = set()
    result: list[tuple[int, int, str]] = []
    for (A, B) in all_edges:
        # Keep the edge only if B does NOT post-dominate A.
        if B != A and B in pdom[A]:
            continue
        stop = ipdom.get(A)
        label = label_of[(A, B)]
        cur = B
        while cur is not None and cur != stop:
            key = (A, cur, label)
            if key not in seen:
                seen.add(key)
                result.append(key)
            cur = ipdom.get(cur)
    return result, _ENTRY


def build_cdg(cfg: Graph) -> Graph:
    """Build the control dependence subgraph as a drawable Graph."""
    deps, entry = control_dependences(cfg)

    g = Graph("CDG", edge_style="dashed")
    idmap: dict[int, int] = {entry: g.add_node("ENTRY", "entry")}

    # Recreate every real statement/predicate node; START and STOP are omitted
    # from the control dependence subgraph, as in the paper.
    for nid, node in cfg.nodes.items():
        if nid in (cfg.entry, cfg.exit):
            continue
        idmap[nid] = g.add_node(node.label, node.kind)

    for (A, B, label) in deps:
        if B in (cfg.entry, cfg.exit):   # never point at START/STOP
            continue
        if A in idmap and B in idmap:
            g.add_edge(idmap[A], idmap[B], label)
    return g