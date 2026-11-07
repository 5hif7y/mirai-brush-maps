# brush_maps: brush maps for Mirai, in one plugin

A plugin for the Mirai engine editor that brings four plugins in one install, as its companions:

| Plugin | What it gives |
| --- | --- |
| [valve220](https://github.com/5hif7y/mirai-valve220) | Imports `.map` files in the Valve 220 dialect (TrenchBroom, J.A.C.K., the Hammer of GoldSrc) as static meshes with collision and materials. |
| [map_convert](https://github.com/5hif7y/mirai-map-convert) | Imports `.vmf` of Hammer, `.map` of Doom 3 and of standard Quake, and `.bsp` of Quake III and Source, through Valve 220; converts them and unpacks WADs from the API. |
| [map_agent](https://github.com/5hif7y/mirai-map-agent) | API for an agent that writes a map in two passes: a structure from rooms and corridors, and a check between passes. |
| [bsp_decompile](https://github.com/5hif7y/mirai-bsp-decompile) | Imports the BSPs of Quake (29), GoldSrc (30) and BSP2, decompiled to brushes. |

Each one is its own repository, with its code, its README, its tests and its history, and is here as a
git subtree in `plugins/<name>/`, the folder where the engine finds the companions of a plugin: the files
are in this repository, and the commit each one comes from is in the history. The catalog lists only
`brush_maps`.

## Install

```sh
mirai plugin add brush_maps
```

The four companions are installed, updated and removed with it, and are active when it is. A project
that already has one of them installed alone cannot add `brush_maps`, and the other way round: their
names would be repeated.

## API

The methods of its companions, by their names:

- `map_convert.to_valve220 {path, out}`: a map of another engine to a Valve 220 `.map` in the project.
- `map_convert.unpack_wad {path, out}`: the textures of a WAD2 or WAD3 as PNG files in the project.
- `map_agent.layout {layout, out}`: rooms and corridors written as JSON to the brushes of a closed
  shell.
- `map_agent.check {path, base}`: walks from the spawns to the objectives, looks for leaks, measures the
  walk of each team and, with `base`, checks that the structure was kept.
- `bsp_decompile.to_valve220 {path, out}`: a BSP of Quake or GoldSrc to a Valve 220 `.map`.

## How it is kept

A fix goes to the repository of its plugin. Then this one brings it:

```sh
git subtree pull --prefix plugins/<name> https://github.com/5hif7y/mirai-<name>.git main --squash
```

`<name>` with hyphens in the address: `mirai-map-convert` for `map_convert`. The squashed commit names the
commit of the plugin it comes from. A change made here, in `plugins/<name>/`, goes back to its repository
with `git subtree push --prefix plugins/<name> <address> <branch>`.

The packages of the four import each other by relative path, so the same files build installed alone
(`plugins/<name>`) and here (`plugins/brush_maps/plugins/<name>`).

## Tests

With `mirai test` of each package of the companions, as their READMEs say, from
`plugins/brush_maps/plugins/<name>/editor`.

## License

Licensed under either of [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option, like each of
its companions. The decompilation method of `bsp_decompile` is the one of
[ericw-tools](https://github.com/ericwa/ericw-tools), by Eric Wasylishen and its contributors; its README
says how.
