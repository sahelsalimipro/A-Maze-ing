# A-Maze-ing

A terminal maze generator and viewer. It carves a maze from a seed, solves it,
writes it to a file in hexadecimal format, and displays it full-screen in the
terminal with an animated theme and an interactive menu.

## Quick start

Requirements: Python 3.13+ and `python-dotenv`. The terminal must support
24-bit color.

```sh
pip install python-dotenv
make run            # same as: python a_maze_ing.py
```

Settings are read from [.env](.env) (see [Configuration](#configuration)).

### Controls

| Key | Action |
|---|---|
| `c` | Switch to the next color palette |
| `s` | Show / hide the solution path |
| `r` | Rebuild the maze from the current seed |
| `n` | Rebuild the maze with a new random seed |
| `t` | Turn the theme on / off |
| `y` | Switch to the next theme |
| `e` or `Ctrl-C` | Quit |
| `↑` `↓` `j` `k` `PgUp` `PgDn`, mouse wheel | Scroll, when the layout is taller than the terminal |

### Make targets

| Target | What it does |
|---|---|
| `make run` | Runs the program |
| `make debug` | Runs it under `pdb` |
| `make lint` / `make lint-strict` | `flake8` and `mypy` (normal or `--strict`) |
| `make build` | Builds the wheel of the maze package into the project root |
| `make clean` | Deletes caches and build output |

## How it runs

```
a_maze_ing.py
  ├─ config.load_config()          read and check .env
  ├─ themes_loader.activate_theme() load the theme, apply its overrides
  ├─ app.build_regions()            cut the screen into regions
  ├─ app.build_maze()               carve, solve, write maze.txt
  ├─ app.attach_drawers()           one drawer per region, from the theme
  └─ render.run()                   main loop: input → simulate → draw
```

## Project layout

### Entry point and app state

- **[a_maze_ing.py](a_maze_ing.py)**: entry point. Loads the configuration,
  builds everything once, then hands over to `render.run()`. Errors during
  configuration stop the program before the screen is taken over.
- **[app.py](app.py)**: the operations that (re)build the program state. Both
  startup and the menu commands use them:
  - `build_maze()` creates a maze from the config, solves it and writes the output file.
  - `build_regions()` computes the layout.
  - `attach_drawers()` gives each region its drawer from the current theme.
  - `switch_theme()` applies a theme change.
- **[globals.py](globals.py)**: shared state and constants: the config, the
  current maze, theme and regions, the frame rate, the terminal size, the scroll
  offset, and the wall-junction characters.

### Configuration

- **[config.py](config.py)**: reads `.env` into a `Settings` object. Each key
  has a type, a default, and two flags:
  - **critical**: a bad value stops the program. Otherwise a warning is logged
    and the default is used.
  - **themeable**: a theme is allowed to override it.

  `Settings` looks values up in three layers: runtime changes (menu commands),
  then theme overrides, then `.env`.
- **[.env](.env)**: every setting, with comments: maze size, seed, perfect or
  not, entry and exit, algorithms, layout, characters, colors, banner and theme.
- **[errors.py](errors.py)**: `ConfigErr`, cross-setting checks (`validate`),
  and a debug check that the regions line up.
- **[logger.py](logger.py)**: warnings go to `amazeing.log`. The terminal is
  busy with the maze, so nothing is printed while it runs.

### The maze: [maze/](maze/)

A standalone package with no dependency on the rest of the project. It is
packaged on its own with `make build`.

- **[amazeing.py](maze/amazeing.py)**: the `Maze` class. Builds the grid (with
  a ring of border tiles and the "42" logo in the center), picks the entry and
  exit, carves, and `resolve()` marks the solution path.
- **[tiles.py](maze/tiles.py)**: tile types. `Tile` is a normal cell, `Limit`
  is the outer border, and `LogoTile` is a cell of the 42 logo that is never
  carved. Each tile knows its walls and neighbours.
- **[dirs.py](maze/dirs.py)**: directions (`N`, `E`, `S`, `W`), their opposites
  and their `(dx, dy)` steps.
- **[carve/](maze/carve/)**: maze generation.
  - `dfs`: randomized depth-first search. Gives long, winding corridors.
  - `wilson`: Wilson's algorithm (loop-erased random walks). Gives uniform,
    unbiased mazes.
  - `utils`: carving helpers. `braid()` adds loops for imperfect mazes
    (`PERFECT=FALSE`) without creating open 2×2 areas.
  - `endpoints`: places the entry and exit, from the config or automatically.
- **[solvers.py](maze/solvers.py)**: shortest path with `bfs` or `astar`.
- **[errors.py](maze/errors.py)**: `MazeErr` and `InvalidTileErr`.

### Output file

- **[output_file.py](output_file.py)**: writes the maze to `OUTPUT_FILE`
  (`maze.txt` by default), using:
  - one hex digit per cell, the sum of its closed walls (N=1, E=2, S=4, W=8);
  - a blank line;
  - the entry coordinates, then the exit coordinates;
  - the shortest path as a string of letters such as `EESSW`.

### Layout: regions and pixels

The screen is split into **regions**, each filled by one **drawer**:

```
┌────────────┬───────────┬──────────────┬────────────┬─────────────┐
│ extra-left │ padd-left │ padd-top     │ padd-right │ extra-right │
│            │           │ banner       │            │             │
│            │           │ maze         │            │             │
│            │           │ padd-bottom  │            │             │
├────────────┴───────────┴──────────────┴────────────┴─────────────┤
│ menu                                                             │
└──────────────────────────────────────────────────────────────────┘
```

- **[dimensions.py](dimensions.py)**: computes the position and size of every
  region from the maze size, `TILE_RATIO` (characters per maze cell),
  paddings, centering and the terminal width.
- **[regions.py](regions.py)**: `Region` owns a pixel buffer and a set of
  "dirty" pixels that changed since the last frame. `redraw()` rebuilds the
  buffer from scratch, `update()` advances the animation.
- **[pixels.py](pixels.py)**: `Pixel` is one character with a foreground and a
  background color. `px_to_str()` turns it into an ANSI escape string.

### Drawing: [drawers/](drawers/)

A drawer has two methods:
- `draw(buffer, config)`: paints the whole buffer. Called on startup and after
  each menu command.
- `update(buffer, dt, mark)`: animates. Every changed pixel is reported with
  `mark(x, y)`.

Files:
- **[base.py](drawers/base.py)**: the `Drawer` interface, `EmptyDrawer`, and
  `MenuDrawer` (the list of actions).
- **[maze_drawer.py](drawers/maze_drawer.py)**: draws the maze. Walls with
  joined box-drawing characters, the solution trail, the entry and exit
  markers, and the 42 logo in block characters.
- **[utils.py](drawers/utils.py)**: helpers for centering, repeating patterns,
  pasting sprites, and converting between maze cells and buffer positions.
- **[art_loader.py](art_loader.py)**: reads `.pxart` pixel-art files (a small
  binary format) and stamps them onto a buffer.

### Themes: [themes/](themes/) and [themes_loader.py](themes_loader.py)

A theme is a package in `themes/` that provides:
- `register(config, maze)`, which returns a drawer for every region;
- optionally, `OVERRIDES`, a dict of themeable settings (colors, paddings,
  banner…).

[themes_loader.py](themes_loader.py) is the only place that decides whether a
theme is valid. It lists the available themes, picks the active one
(`THEME_NAME` if `THEME_ON`, otherwise `default`), and runs `register()`.

| Theme | Description |
|---|---|
| `default` | Solid colored paddings, a framed banner, and the maze |
| `matrix` | Falling green "digital rain" on the sides with quotes inside it, and animated strips above and below |
| `pac_man` | Work in progress. Skipped until it defines `register()` |

To add a theme, create `themes/<name>/__init__.py` with a `register()`
function. It shows up in the `y` cycle automatically.

### Menu and input: [menu/](menu/)

- **[keyboard.py](menu/keyboard.py)**: non-blocking key reading, for Linux,
  macOS and Windows. Turns arrow and page keys into `"UP"`, `"DOWN"`,
  `"PGUP"`, `"PGDN"`.
- **[commands.py](menu/commands.py)**: the list of commands (key, name,
  description, function, optional indicator).
- **[input_commands.py](menu/input_commands.py)**: what each command does. A
  command changes the config or the app state, then returns `True` to ask for a
  full redraw.
- **[inputs.py](menu/inputs.py)**: sends each key to scrolling or to a
  command. Returns how much needs redrawing: nothing, a repaint (scroll), or a
  rebuild (command).
- **[indicators.py](menu/indicators.py)**: the live values shown in the menu
  (`ON`/`OFF`, theme name).
- **[menu.py](menu/menu.py)**: computes the menu's layout, wrapping text to
  the terminal width.

### Rendering: [render/](render/) and [viewport.py](viewport.py)

- **[render.py](render/render.py)**: the main loop. Each pass reads input,
  advances the animations at a fixed 60 Hz, and outputs a frame at `FPS`.
  - Only dirty pixels are sent, using cursor-positioning escape codes, so the
    terminal never has to redraw everything.
  - Each frame is wrapped in synchronized output, so there's no tearing.
  - The program runs in the terminal's **alternate screen**: the shell is
    restored as it was on exit, even after `Ctrl-C` or a crash.
- **[viewport.py](viewport.py)**: the alternate screen has no scrollback, so
  scrolling is done by the program. `VIEW_Y` is the first layout row shown on
  screen.

### Developer tools: [dev/](dev/)

- **[convert_pixel_art.py](dev/convert_pixel_art.py)**: converts a PNG into a
  `.pxart` file. Needs Pillow, only when you run it.
- **[helper_drawer.py](dev/helper_drawer.py)**: `NumericalDrawer`, which writes
  row and column numbers into a region to check its dimensions.
- **[debug.py](dev/debug.py)**: debugging snippets.
- **[assets/](dev/assets/)**: source images for the pixel art.
- **[TODOlist](dev/TODOlist)**: the team's task list.

## Configuration

Every setting is documented in [.env](.env). The most used:

| Key | Meaning |
|---|---|
| `MAZE_WIDTH`, `MAZE_HEIGHT` | Size in cells (minimum 9×7) |
| `SEED` | Same seed and same settings give the same maze |
| `PERFECT` | `TRUE`: exactly one path between any two cells. `FALSE`: adds loops |
| `ENTRY`, `EXIT` | `x,y` coordinates, or `NONE` to let the program choose |
| `CARVER_ALGO` | `dfs` or `wilson` |
| `SOLVER_ALGO` | `bfs` or `astar` |
| `SOLVED` | Show the solution path at startup |
| `TILE_RATIO` | Characters per cell, horizontally and vertically (e.g. `3,1`) |
| `THEME_ON`, `THEME_NAME` | Theme to use |
| `OUTPUT_FILE` | Where the hex maze is written |

Invalid values are logged in `amazeing.log` and replaced by their default,
except for critical keys (`SEED`, `PERFECT`, algorithms, `TILE_RATIO`), which
stop the program with an error message.
