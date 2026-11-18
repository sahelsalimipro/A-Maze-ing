*This activity has been created as part of the 42 curriculum by ssalimi, banordma.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator and viewer for the terminal. From a
configuration file, it:

1. generates a maze from a seed (same seed and settings, same maze), with a
   "42" drawn in its centre by fully closed cells;
2. makes it either **perfect** (exactly one path between entry and exit) or a
   **Pac-Man-like board** (loops, almost no dead ends);
3. finds the shortest path from the entry to the exit;
4. writes the maze to a file, one hexadecimal digit per cell;
5. displays it full-screen in the terminal, with themes, animations and an
   interactive menu.

The maze generation code is a standalone Python package, `mazegen`, that can
be installed with `pip` and reused in other projects
(see [Reusable code](#reusable-code-the-mazegen-package)).

## Instructions

### Requirements

- Python 3.10 or later (developed and tested with Python 3.14).
- `python-dotenv` (installed by `make install`).
- A terminal that supports 24-bit color and Unicode box-drawing characters.

### Install and run

```sh
make install                     # pip install -r requirements.txt
make run                         # python3 a_maze_ing.py .env
```

The configuration is read from [.env](.env)
(see [Configuration file](#configuration-file)).

### Controls

| Key | Action |
|---|---|
| `c` | Switch to the next color palette (walls, background, path) |
| `s` | Show / hide the shortest path |
| `r` | Rebuild the maze from the current seed |
| `n` | Generate a new maze (new random seed) |
| `t` | Turn the theme on / off |
| `y` | Switch to the next theme |
| `e` or `Ctrl-C` | Quit |
| `↑` `↓` `j` `k` `PgUp` `PgDn`, mouse wheel | Scroll, when the layout is taller than the terminal |

### Make targets

| Target | What it does |
|---|---|
| `make install` | Installs the dependencies |
| `make run` | Runs the program with the default configuration |
| `make debug` | Runs it under `pdb` |
| `make lint` | `flake8` and `mypy` with the flags required by the subject |
| `make lint-strict` | `flake8` and `mypy --strict` |
| `make build` | Builds the `mazegen` package and copies the wheel to the repository root |
| `make clean` | Deletes caches and build output |

## Configuration file

### Format

- One `KEY=VALUE` pair per line.
- Lines starting with `#` are comments. Text after a `#` at the end of a line
  is also ignored.
- Values may be quoted (`BANNER_TITLE="AMAZEING"`).
- Value types:

| Type | Syntax | Example |
|---|---|---|
| int | a whole number | `SEED=42` |
| bool | `TRUE` or `FALSE` (any case) | `PERFECT=FALSE` |
| coordinates | `x,y`, 0-based, `0,0` is the top-left cell; or `NONE` to let the program choose | `ENTRY=0,0` |
| color | `r, g, b` with each value from 0 to 255; or `NONE` for the terminal's default color | `WALLS_CLR=252, 107, 3` |
| ratio | `horizontal,vertical` characters per cell | `TILE_RATIO=3,1` |
| char | a single character | `ENTRYPOINT_CHAR="◇"` |
| str | text | `OUTPUT_FILE=maze.txt` |

Errors are handled in two ways:
- **Required** keys (marked below): a missing or invalid value stops the
  program with an error message.
- Other keys: an invalid value is replaced by its default, and a warning is
  written to `amazeing.log`.

### Maze keys

| Key | Type | Description |
|---|---|---|
| `WIDTH` | int | Width in cells |
| `HEIGHT` | int | Height in cells |
| `ENTRY` | coordinates | Entry cell |
| `EXIT` | coordinates | Exit cell |
| `OUTPUT_FILE` | str | File the maze is written to |
| `PERFECT` | bool | **Required.** `TRUE`: perfect maze. `FALSE`: Pac-Man board |
| `SEED` | int | **Required.** Seed of the random generator |
| `CARVER_ALGO` | str | **Required.** Generation algorithm: `dfs` or `wilson` |
| `SOLVER_ALGO` | str | **Required.** Shortest-path algorithm: `bfs` or `astar` |
| `SOLVED` | bool | Show the shortest path at startup |

### Display keys

| Key | Type | Description |
|---|---|---|
| `THEME_ON` | bool | Use the theme in `THEME_NAME`. `FALSE` uses `default` |
| `THEME_NAME` | str | `default` or `matrix` |
| `TILE_RATIO` | ratio | **Required.** Characters per cell, horizontally and vertically |
| `CENTER_MAZE` | bool | Center the maze horizontally in the terminal |
| `DISPLAY_BANNER` | bool | Show the title banner above the maze |
| `TOP_PADDING`, `BOT_PADDING`, `LEFT_PADDING`, `RIGHT_PADDING` | int | Empty lines / columns around the maze |
| `EXPAND_COLOR_TO_FULL_TERMINAL` | bool | Paint the background color up to the terminal's right edge |
| `ENTRYPOINT_CHAR`, `EXITPOINT_CHAR` | char | Characters marking the entry and the exit |
| `BACKGROUND_CLR`, `WALLS_CLR`, `TRAIL_CLR` | color | Background, walls and shortest-path colors |
| `ENTRYPOINT_CLR`, `EXITPOINT_CLR` | color | Entry and exit colors |
| `TOP_PADDING_CLR`, `BOT_PADDING_CLR`, `LEFT_PADDING_CLR`, `RIGHT_PADDING_CLR` | color | Padding colors |
| `BANNER_TITLE` | str | Text of the banner |
| `BANNER_TITLE_CLR`, `BANNER_FRAME_CLR`, `BANNER_BCKG_CLR` | color | Banner colors |
| `BANNER_TOP_CHAR`, `BANNER_BOT_CHAR`, `BANNER_LEFT_CHAR`, `BANNER_RIGHT_CHAR` | str | Characters of the banner's frame (repeated if longer than one) |
| `BANNER_CORNER_TOPLEFT_CHAR`, `BANNER_CORNER_TOPRIGHT_CHAR`, `BANNER_CORNER_BOTLEFT_CHAR`, `BANNER_CORNER_BOTRIGHT_CHAR` | char | Corners of the banner's frame |

A theme can override most display keys. The comments in [.env](.env) say
which ones.

## Output file

The maze is written to `OUTPUT_FILE`:

- one line per row, one hexadecimal digit per cell. Each digit is the sum of
  its closed walls: North = 1, East = 2, South = 4, West = 8 (`F` = fully
  closed, as in the "42");
- an empty line;
- the entry coordinates, then the exit coordinates (`x,y`);
- the shortest path from entry to exit, as letters `N`, `E`, `S`, `W`.

Every line ends with `\n`.

## Maze generation

### Algorithms

Two algorithms are available, chosen with `CARVER_ALGO`:

- **`dfs`: randomized depth-first search** (the "recursive backtracker"),
  used by default. Start from a cell, move to a random unvisited neighbour
  and remove the wall between them; when stuck, go back until a cell has an
  unvisited neighbour. It produces long, winding corridors.
- **`wilson`: Wilson's algorithm.** Random walks from unvisited cells, with
  their loops erased, until they reach the maze. Every possible perfect maze
  is equally likely, so the result has no visual bias.

Both produce a perfect maze (a spanning tree of the grid). When
`PERFECT=FALSE`, a second step, **braiding**, turns it into a Pac-Man board:
every dead end gets one more wall removed, which creates loops. When that
would open a 2×2 area, another wall of that area is closed instead, so
corridors are never more than one cell wide.

The 42 cells are marked before carving and never carved, so they stay fully
closed and every other cell stays reachable. The 42 is centred on the maze's
centre cell, which is an open cell of the pattern, so the centre is always a
corridor. Mazes smaller than 9×7 have no room for it: they are generated
without the 42, and a warning is written to `amazeing.log`.

The shortest path is found with `SOLVER_ALGO`: breadth-first search (`bfs`)
or A\* with the Manhattan distance (`astar`). Both return a shortest path.

### Why these algorithms

> **TODO (team):** check this reflects your own reasons, and adjust it.

- The recursive backtracker is short to write and easy to explain, and its
  long corridors make mazes that are fun to look at and to solve.
- Wilson's algorithm was added for comparison: it gives uniform mazes, at the
  cost of a longer generation on large grids.
- Braiding after generation lets both algorithms make both kinds of maze, so
  the "perfect" and "Pac-Man" modes don't need separate generators.

## Reusable code: the `mazegen` package

The [maze/](maze/) folder is a standalone package: it only uses the Python
standard library, and nothing in it depends on the rest of the project
(display, configuration, output file). It is packaged as `mazegen`; the wheel
is at the root of the repository (`mazegen-1.0.0-py3-none-any.whl`).

### Install

```sh
pip install mazegen-1.0.0-py3-none-any.whl
```

To rebuild it from the sources (needs `pyproject.toml` and the `maze/`
folder):

```sh
python3 -m venv venv && source venv/bin/activate
pip install build
python3 -m build                  # creates dist/mazegen-1.0.0.tar.gz and .whl
```

The package is installed as `mazegen`, and imported as `maze`.

### Basic example

```python
from maze import Maze

m = Maze(20, 15, seed=42)         # 20x15 cells, reproducible
path = m.resolve()                # shortest path, entry to exit
print(m)                          # ASCII view: S entry, E exit, . path, # 42
```

### Parameters

```python
Maze(
    width, height,                # size in cells
    seed=None,                    # int for a reproducible maze, None for random
    perfect=True,                 # False: Pac-Man board with loops
    entry=None, exit=None,        # (x, y), 0-based; None to choose automatically
    carver="dfs",                 # "dfs" or "wilson"
    solver="bfs",                 # "bfs" or "astar"
)
```

Invalid parameters (an entry on the 42, entry equal to exit…) raise
`maze.MazeErr` with a readable message.

### Accessing the structure

`m.grid` is a list of rows, each a list of tiles, indexed `m.grid[y][x]`.
The grid has a one-tile border ring, so the maze's cell `(x, y)` is
`m.grid[y + 1][x + 1]`.

Each tile has:

| Attribute | Meaning |
|---|---|
| `x`, `y` | Grid coordinates (subtract 1 for maze coordinates) |
| `walls` | `{"N": bool, "E": bool, "S": bool, "W": bool}`, `True` = closed |
| `neighbours` | `{"N": tile, ...}`, the adjacent tiles |
| `isLogo` | `True` for the cells of the "42" |
| `isSolution` | `True` for the cells of the path, after `resolve()` |

```python
for row in m.grid[1:-1]:          # skip the border ring
    for tile in row[1:-1]:
        print(tile.x - 1, tile.y - 1, tile.walls)
```

### Accessing the solution

```python
path = m.resolve()                # list of tiles, from m.entry to m.exit
coords = [(t.x - 1, t.y - 1) for t in path]
```

`m.entry` and `m.exit` are the entry and exit tiles.

## Advanced features

- **Two generation algorithms** (`dfs`, `wilson`) and **two solvers**
  (`bfs`, `astar`), chosen in the configuration.
- **Themes**: `default` (solid colors and a framed banner) and `matrix`
  (falling green "digital rain" with quotes hidden in it). A theme is a folder
  in `themes/` with a `register()` function; it appears in the `y` cycle
  automatically. A `pac_man` theme is in progress.
- **Animated, full-screen rendering**: only the characters that changed are
  redrawn, each frame is sent at once (no flickering), and the terminal is
  restored on exit, even after `Ctrl-C` or an error.
- **Scrolling** when the maze is taller than the terminal.
- **Configurable display**: colors, characters, paddings, cell size, banner.

## Project structure

```
a_maze_ing.py
  ├─ config.load_config()           read and check the configuration file
  ├─ themes_loader.activate_theme() load the theme, apply its overrides
  ├─ app.build_regions()            cut the screen into regions
  ├─ app.build_maze()               generate, solve, write the output file
  ├─ app.attach_drawers()           one drawer per region, from the theme
  └─ render.run()                   main loop: input → animate → draw
```

| Path | Contents |
|---|---|
| [a_maze_ing.py](a_maze_ing.py) | Entry point |
| [app.py](app.py) | Builds and rebuilds the maze, layout and drawers (used at startup and by the menu) |
| [config.py](config.py), [errors.py](errors.py) | Reading and checking the configuration |
| [maze/](maze/) | The reusable `mazegen` package: `Maze`, tiles, carvers, solvers |
| [output_file.py](output_file.py) | Writes the hexadecimal output file |
| [dimensions.py](dimensions.py), [regions.py](regions.py), [pixels.py](pixels.py) | Screen layout: regions made of colored characters |
| [drawers/](drawers/) | Draw the maze and the menu into a region |
| [themes/](themes/), [themes_loader.py](themes_loader.py) | Themes and how they are loaded |
| [menu/](menu/) | Keyboard input, commands and menu layout |
| [render/](render/), [viewport.py](viewport.py) | Main loop, terminal output, scrolling |
| [dev/](dev/) | Developer tools (pixel-art converter, debug helpers), not used at runtime |

## Team and project management

> **TODO (team):** fill in this section; only you know it.

### Roles

- **ssalimi**: TODO (e.g. which parts you designed and wrote)
- **banordma**: TODO

### Planning

- **Initial plan**: TODO (the steps and the order you had planned)
- **How it evolved**: TODO (what took longer, what was added or dropped,
  for example the Pac-Man mode and the themes)

### What worked well, what could be improved

- TODO
- TODO

### Tools

- Git and GitHub, `make`, `flake8`, `mypy`, `autopep8`, Python `venv`,
  `build`.
- VS Code.
- TODO: add anything else you used (task list in [dev/TODOlist](dev/TODOlist),
  communication, etc.).

## Resources

### References

- [Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm),
  Wikipedia: overview of DFS, Wilson's, Prim's and Kruskal's algorithms.
- Jamis Buck, [Maze Generation: Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
  and [Maze Generation: Wilson's algorithm](https://weblog.jamisbuck.org/2011/1/20/maze-generation-wilson-s-algorithm).
- Jamis Buck, *Mazes for Programmers*, Pragmatic Bookshelf, 2015 (braid
  mazes, dead-end removal).
- David B. Wilson, *Generating random spanning trees more quickly than the
  cover time*, STOC 1996.
- [A\* search algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)
  and [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search),
  Wikipedia.
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/):
  `pyproject.toml`, building wheels.
- [ANSI escape code](https://en.wikipedia.org/wiki/ANSI_escape_code),
  Wikipedia: colors, cursor movement, alternate screen.
- [mypy](https://mypy.readthedocs.io/) and [flake8](https://flake8.pycqa.org/)
  documentation.

### Use of AI

> **TODO (team):** complete this list with every other use of AI in the
> project (the subject asks which tasks and which parts), and keep the
> last sentence only if it is true.

AI (Claude, in VS Code) was used for:

- **Packaging**: finding why the first wheel was empty (`pyproject.toml`
  looked for a `mazegen` folder instead of `maze`), and how to test the wheel
  in a separate virtual environment.
- **Linting**: fixing the `mypy` errors in `menu/commands.py` and
  `themes/default/__init__.py`, and the `flake8` style errors (line length,
  blank lines, unused imports) across the project.
- **Small additions to `Maze`**: the ASCII `__repr__`, and the `entry`,
  `exit` properties and returned path of `resolve()`, for the package
  documentation.
- **Tooling**: setting up the VS Code formatter extension.
- **Review**: checking the project against the subject, and restructuring
  this README to include the required sections.

All generated code was reviewed, tested and is understood by the team.
