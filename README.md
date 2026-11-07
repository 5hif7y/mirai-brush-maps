# brush_maps: brush maps for Mirai, in one plugin

A plugin for the Mirai engine editor that joins three plugins in one install:

| Plugin | What it gives |
| --- | --- |
| [valve220](https://github.com/5hif7y/mirai-valve220) | Imports `.map` files in the Valve 220 dialect (TrenchBroom, J.A.C.K., the Hammer of GoldSrc) as static meshes with collision and materials. |
| [map_convert](https://github.com/5hif7y/mirai-map-convert) | Imports `.vmf` of Hammer, `.map` of Doom 3 and of standard Quake, and `.bsp` of Quake III and Source, through Valve 220; converts them and unpacks WADs from the API. |
| [map_agent](https://github.com/5hif7y/mirai-map-agent) | API for an agent that writes a map in two passes: a structure from rooms and corridors, and a check between passes. |

The three remain plugins of their own, for a project that wants only one of them. The code is the
same: this repository is assembled from theirs, at the commits that `SOURCES.json` names, and the
README of each says what it reads and what was measured.

## Install

```sh
mirai plugin add brush_maps
```

Install either `brush_maps` or the plugins it joins, not both: the formats would be registered twice.
[bsp_decompile](https://github.com/5hif7y/mirai-bsp-decompile), the BSPs of Quake and GoldSrc, is not
in this plugin: it is under the GPL and depends on `valve220` and `map_convert`, so it goes with the
separate plugins.

## API

The methods of `map_convert` and `map_agent` with the prefix of this plugin:

- `brush_maps.to_valve220 {path, out}`: a map of another engine to a Valve 220 `.map` in the project.
- `brush_maps.unpack_wad {path, out}`: the textures of a WAD2 or WAD3 as PNG files in the project.
- `brush_maps.layout {layout, out}`: rooms and corridors written as JSON to the brushes of a closed shell.
- `brush_maps.check {path, base}`: walks from the spawns to the objectives, looks for leaks, measures
  the walk of each team and, with `base`, checks that the structure was kept.

The parameters and results are those of the separate plugins.

## How it is assembled

```sh
python3 tools/assemble.py <valve220> <map_convert> <map_agent>
```

Each argument is a checkout of that plugin, at a commit without local changes. The script copies their
`editor/` packages, renames packages and import paths to `brush_maps`, joins the three root packages in
one and renames the methods; it writes `editor/`, `examples/` and `SOURCES.json`. A fix goes to the
plugin it belongs to, and then the script runs again here.

## Tests

With `mirai test` of `plugins/brush_maps/editor` and of its packages `loader`, `formats` and `agent`:
the tests of the three plugins it joins. The maps of the tests are built in code.

## License

Licensed under either of [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option.
