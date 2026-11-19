# GpufxVideoEditor-Assets-capcut

Clip animation packs for [GpufxVideoEditor](https://github.com/tqk2811/GpufxVideoEditor): in, out
and loop presets that move, scale, turn and fade a clip.

Recreated and optimized with reference to CapCut's resources. Only motion parameters (durations,
easings, amplitudes, start and end values) were used as reference, and every curve is written by
hand as JSON. This repository holds no CapCut files: no assets, code, shaders, fonts or images.
CapCut is a trademark of its owner, and this project is not affiliated with it.

## Packs

| Zip | Applies to | Contents |
|---|---|---|
| `capcut-anim-basic.zip` | every clip | zoom, mini zoom, slides in four directions, spin out, pulse, shake, flash |
| `capcut-anim-text.zip` | text | shrink in/out, spin in, jump, bob |
| `capcut-anim-sticker.zip` | sticker | fade in/out, rotate, flip |

The sources are `animations/<pack>/pack.json` (id, name, version and `items`, the item ids in order)
and one `animations/<pack>/items/<id>.json` per item. The id of an item is its file name; a listed id
without a file, a file that is not listed and a duplicate id are errors. Each item has a `description`
that names the CapCut preset it recreates; the description stays in the source and is not part of the
zip. A zip has `manifest.json` (`items` = the item ids) and `items/<id>.json`, next to the licence files.

Moves are in parts of the output frame. CapCut moves by a multiple of the clip size, so these packs
use a reference clip of 0.3 of the frame. Turns are in degrees, clockwise.

## Build

```sh
python scripts/pack.py           # dist/<pack id>.zip for every pack
python scripts/pack.py --check   # validate the sources only
```

Only the Python standard library is needed. The zips are reproducible byte for byte, and each
manifest and item is checked against the rules of the editor's strict pack reader (including the ease
forms `power`, `elastic`, `bounce`, `steps` and `wave` with their parameter ranges) before it is written.

## Install

Download a zip from the [releases](https://github.com/tqk2811/GpufxVideoEditor-Assets-capcut/releases)
and import it in GpufxVideoEditor as a package. A tag `vX.Y.Z` builds and publishes the release.

## License

MIT, see [LICENSE](LICENSE).
