#!/usr/bin/env python3
"""pdg - build dependence graphs from a small Python-subset program.

Usage examples:
    python pdg.py examples/ex2_control.py                 # CFG (default)
    python pdg.py examples/ex2_control.py --graph cfg
    python pdg.py examples/ex2_control.py --graph all --out out/

Each requested graph is written as a Graphviz .dot file, and (if the
Graphviz `dot` program is installed) rendered to .png alongside it.

Phase 2 implements the CFG. The CDG (--graph cdg) and DDG (--graph ddg)
are placeholders until Phases 3 and 4.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

from pdgtool.cfg import build_cfg
from pdgtool.frontend import SubsetError, parse_file, validate
from pdgtool.graph import Graph


def render(graph: Graph, out_base: str) -> None:
    """Write ``out_base.dot`` and try to produce ``out_base.png``."""
    dot_path = out_base + ".dot"
    with open(dot_path, "w", encoding="utf-8") as fh:
        fh.write(graph.to_dot())
    print(f"  wrote {dot_path}")

    try:
        subprocess.run(
            ["dot", "-Tpng", dot_path, "-o", out_base + ".png"],
            check=True,
            capture_output=True,
        )
        print(f"  wrote {out_base}.png")
    except FileNotFoundError:
        print("  (Graphviz 'dot' not found - install it with: sudo apt install graphviz)")
    except subprocess.CalledProcessError as exc:
        print(f"  (dot failed: {exc.stderr.decode().strip()})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="pdg",
        description="Parse a Python-subset program and emit its dependence graphs.",
    )
    ap.add_argument("source", help="path to the input program")
    ap.add_argument(
        "--graph",
        choices=["cfg", "cdg", "ddg", "all"],
        default="cfg",
        help="which graph to build (default: cfg)",
    )
    ap.add_argument(
        "--out",
        default="out",
        help="output directory for .dot/.png files (default: out/)",
    )
    args = ap.parse_args(argv)

    # Front end: parse and enforce the accepted subset.
    try:
        tree = parse_file(args.source)
        validate(tree, args.source)
    except SubsetError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"error: no such file: {args.source}", file=sys.stderr)
        return 1

    os.makedirs(args.out, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.source))[0]
    base = os.path.join(args.out, stem)

    want = args.graph
    if want in ("cfg", "all"):
        print("CFG:")
        render(build_cfg(tree), base + "_cfg")
    if want in ("cdg", "all"):
        print("CDG: not implemented yet (Phase 3 - control dependence).")
    if want in ("ddg", "all"):
        print("DDG: not implemented yet (Phase 4 - data dependence).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())