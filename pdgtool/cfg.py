"""Control flow graph construction (Phase 2).

Nodes are at the statement / predicate level, matching the paper's figures:
every simple statement is one node, every ``if``/``while`` test is a
predicate node with True and False out-edges, and there are unique START
(entry) and STOP (exit) nodes as required by Definition 1.

The builder threads a "fringe" through the AST: a list of (node, edge_label)
pairs that still need an out-edge to whatever statement comes next. This
handles branches merging and loops closing without any special cases.
"""

from __future__ import annotations

import ast

from .graph import Graph

Fringe = list  # list[tuple[int, str]] of (node_id, edge_label)


def build_cfg(tree: ast.Module) -> Graph:
    g = Graph("CFG", edge_style="solid")
    entry = g.add_node("START", "entry")
    exit_ = g.add_node("STOP", "exit")
    g.entry, g.exit = entry, exit_

    fringe: Fringe = [(entry, "")]
    fringe = _process_block(tree.body, g, fringe)

    # Anything still dangling flows to STOP.
    _connect(g, fringe, exit_)
    return g


def _src(node: ast.AST) -> str:
    """Best-effort source text for a node label."""
    try:
        return ast.unparse(node).strip()
    except Exception:  # pragma: no cover - unparse is very reliable on 3.9+
        return type(node).__name__


def _connect(g: Graph, fringe: Fringe, target: int) -> None:
    for (src, label) in fringe:
        g.add_edge(src, target, label)


def _process_block(stmts: list[ast.stmt], g: Graph, fringe: Fringe) -> Fringe:
    for stmt in stmts:
        fringe = _process_stmt(stmt, g, fringe)
    return fringe


def _process_stmt(stmt: ast.stmt, g: Graph, fringe: Fringe) -> Fringe:
    if isinstance(stmt, ast.If):
        pred = g.add_node(_src(stmt.test), "predicate")
        _connect(g, fringe, pred)
        then_fringe = _process_block(stmt.body, g, [(pred, "T")])
        if stmt.orelse:
            # elif is represented by Python as an If nested in orelse, so this
            # single recursive call handles elif chains automatically.
            else_fringe = _process_block(stmt.orelse, g, [(pred, "F")])
            return then_fringe + else_fringe
        return then_fringe + [(pred, "F")]

    if isinstance(stmt, ast.While):
        pred = g.add_node(_src(stmt.test), "predicate")
        _connect(g, fringe, pred)
        body_fringe = _process_block(stmt.body, g, [(pred, "T")])
        _connect(g, body_fringe, pred)  # loop back-edge to the test
        return [(pred, "F")]            # the False exit leaves the loop

    # Any other statement (assignment, print, expression) is one plain node.
    node = g.add_node(_src(stmt), "stmt")
    _connect(g, fringe, node)
    return [(node, "")]