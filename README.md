# PDG Tool

A command-line tool that parses a small Python-subset program and builds its
dependence graphs. Part of the Program Dependence Graph based optimization
project (based on Ferrante, Ottenstein & Warren, 1987).

## Status

- Phase 2 (done): front end + control flow graph (CFG).
- Phase 3 (done): control dependence graph (CDG).
- Phase 4 (todo): data dependence graph (DDG).

## Setup

Requires Python 3.9+ (uses `ast.unparse`) and, for PNG output, Graphviz:

```bash
sudo apt install graphviz
```

No Python packages need to be installed; the tool uses only the standard library.

## Usage

Run from the project root:

```bash
python pdg.py examples/ex2_control.py                  # CFG (default)
python pdg.py examples/ex2_control.py --graph cfg
python pdg.py examples/ex4_fibonacci.py --graph all    # CFG now, CDG/DDG later
python pdg.py examples/ex3_loop.py --out out/          # choose output dir
```

Each graph is written as a `.dot` file and, if Graphviz is installed, rendered
to `.png` beside it in the output directory (default `out/`).

Programs that use constructs outside the accepted subset (for loops, functions,
lists, and so on) are rejected with a line-numbered error.

## Layout

```
pdg.py              command-line entry point
pdgtool/
  frontend.py       parse a file and validate the accepted subset
  cfg.py            control flow graph construction
  postdom.py        post-dominator tree (support for control dependence)
  cdg.py            control dependence graph construction
  graph.py          shared graph type + Graphviz rendering
examples/           the four Phase 1 example programs
```