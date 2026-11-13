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
| `capcut-anim-video.zip` | video, image | blur, zoom blur, wipe and slide in four directions, clock wipe, in and out, each running a shader package |

The sources are `animations/<pack>/pack.json`. Each item has a `description` that names the
CapCut preset it recreates; the description stays in the source and is not part of the manifest.

Moves are in parts of the output frame. CapCut moves by a multiple of the clip size, so these packs
use a reference clip of 0.3 of the frame. Turns are in degrees, clockwise.

## Shader packages

Animations that change pixels rather than move the clip are gpufx effect packages in
`packages/gpufx/capcut-anim/<name>/` (manifest and WGSL shaders, see the gpufx effect format). Each
has one input and a float `progress`: 0 is the start of the in animation, 1 is the untouched clip.
The editor drives `progress` from 0 to 1 for an in animation and from 1 to 0 for an out one. Every
package is one compute pass. They are written anew from how the animations look.

| Zip | Params besides `progress` |
|---|---|
| `io.github.tqk2811.capcut-anim.directional-blur.zip` | `angle` (degrees), `strength` |
| `io.github.tqk2811.capcut-anim.zoom-blur.zip` | `scale` (start scale), `strength`, `center` |
| `io.github.tqk2811.capcut-anim.wipe.zip` | `direction` (right, left, down, up), `feather` |
| `io.github.tqk2811.capcut-anim.clock-wipe.zip` | `start_angle`, `clockwise`, `feather`, `center` |
| `io.github.tqk2811.capcut-anim.slide.zip` | `direction`, `distance` (frames, mirror wrapped), `motion_blur` |

`capcut-anim-video` items have an `effect` instead of a `curve`: `{package, progress?, params?}`. An
in item drives `progress` from 0 to 1, an out item from 1 to 0, a loop item by its phase. `params` hold
numbers, bools, 2 to 4 numbers, or for an enum param the name of one of its values (`wipe` and `slide`
set `direction` to right, left, down or up, one item each). `scripts/pack.py` checks the package id against the packages
of this repository, and the params against the manifest of that package.

The wipes work through alpha. The blurs average in premultiplied alpha, so transparent edges stay
clean.

## Build

```sh
python scripts/pack.py           # dist/<pack id>.zip for every pack and shader package
python scripts/pack.py --check   # validate the sources only
```

Only the Python standard library is needed. The zips are reproducible byte for byte, and each
manifest is checked against the rules of the editor's strict pack reader before it is written.

## Install

Download a zip from the [releases](https://github.com/tqk2811/GpufxVideoEditor-Assets-capcut/releases)
and import it in GpufxVideoEditor as a package. A tag `vX.Y.Z` builds and publishes the release.

## License

MIT, see [LICENSE](LICENSE).
