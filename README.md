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
| `capcut-anim-text.zip` | text | shrink in/out, spin in, jump |
| `capcut-anim-sticker.zip` | sticker | fade in/out, rotate, flip |

The sources are `animations/<pack>/pack.json`. Each item has a `description` that names the
CapCut preset it recreates; the description stays in the source and is not part of the manifest.

Moves are in parts of the output frame. CapCut moves by a multiple of the clip size, so these packs
use a reference clip of 0.3 of the frame. Turns are in degrees, clockwise.

## Build

```sh
python scripts/pack.py           # dist/<pack id>.zip for every pack
python scripts/pack.py --check   # validate the sources only
```

Only the Python standard library is needed. The zips are reproducible byte for byte, and each
manifest is checked against the rules of the editor's strict pack reader before it is written.

## Install

Download a zip from the [releases](https://github.com/tqk2811/GpufxVideoEditor-Assets-capcut/releases)
and import it in GpufxVideoEditor as a package. A tag `vX.Y.Z` builds and publishes the release.

## License

MIT, see [LICENSE](LICENSE).
