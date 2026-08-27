"""A tiny directed-graph structure shared by every phase, plus DOT output.

Keeping one Graph type for the CFG, the control dependence graph, and the
data dependence graph means the renderer is written once and every phase
draws in a consistent style.
"""

from __future__ import annotations


# Node kinds understood by the renderer. Later phases add "region".
_SHAPES = {
    "entry": ("ellipse", "#d9e1f2"),
    "exit": ("ellipse", "#d9e1f2"),
    "predicate": ("diamond", "#fce4d6"),
    "stmt": ("box", "#ffffff"),
    "region": ("ellipse", "#e2efda"),
}


class Node:
    def __init__(self, nid: int, label: str, kind: str):
        self.id = nid
        self.label = label
        self.kind = kind

    def __repr__(self) -> str:
        return f"Node({self.id}, {self.kind}, {self.label!r})"


class Graph:
    """A directed graph with labelled edges.

    Edge style is chosen at render time by ``edge_style``: control flow and
    control dependence differ (dashed vs solid) in the paper's figures, so
    each phase can pass its own style without changing this class.
    """

    def __init__(self, name: str = "G", edge_style: str = "solid"):
        self.name = name
        self.edge_style = edge_style
        self.nodes: dict[int, Node] = {}
        self.edges: list[tuple[int, int, str]] = []
        self.entry: int | None = None
        self.exit: int | None = None
        self._counter = 0

    def add_node(self, label: str, kind: str) -> int:
        self._counter += 1
        nid = self._counter
        self.nodes[nid] = Node(nid, label, kind)
        return nid

    def add_edge(self, src: int, dst: int, label: str = "") -> None:
        self.edges.append((src, dst, label))

    def successors(self, nid: int) -> list[int]:
        return [d for (s, d, _) in self.edges if s == nid]

    def predecessors(self, nid: int) -> list[int]:
        return [s for (s, d, _) in self.edges if d == nid]

    # -- rendering ----------------------------------------------------------
    def to_dot(self) -> str:
        lines = [f'digraph "{self.name}" {{']
        lines.append('  rankdir=TB;')
        lines.append('  node [fontname="Helvetica", fontsize=10];')
        lines.append('  edge [fontname="Helvetica", fontsize=9];')
        for nid, node in self.nodes.items():
            shape, fill = _SHAPES.get(node.kind, ("box", "#ffffff"))
            label = _escape(node.label)
            lines.append(
                f'  n{nid} [label="{label}", shape={shape}, '
                f'style="filled", fillcolor="{fill}"];'
            )
        for (src, dst, elabel) in self.edges:
            attrs = [f'style={self.edge_style}']
            if elabel:
                attrs.append(f'label="{_escape(elabel)}"')
            lines.append(f'  n{src} -> n{dst} [{", ".join(attrs)}];')
        lines.append("}")
        return "\n".join(lines) + "\n"


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')