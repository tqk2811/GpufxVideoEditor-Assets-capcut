# GpufxVideoEditor-Assets-capcut

Clip animation packs for [GpufxVideoEditor](https://github.com/tqk2811/GpufxVideoEditor): in, out
and loop presets that move, scale, turn and fade a clip.

Recreated and optimized with reference to CapCut's resources. Only motion parameters (durations,
easings, amplitudes, start and end values) were used as reference, and every curve is written by
hand as JSON. This repository holds no CapCut files: no assets, code, shaders, fonts or images.
CapCut is a trademark of its owner, and this project is not affiliated with it.

## Packs

| Collection | Packs | Applies to | Contents |
|---|---|---|---|
| `capcut-anim-basic` | 16 | every clip | zoom, mini zoom, slides in four directions, spin out, pulse, shake, flash |
| `capcut-anim-text` | 5 | text | shrink in/out, spin in, jump, bob |
| `capcut-anim-sticker` | 4 | sticker | fade in/out, rotate, flip |

The sources are `animations/<pack>/pack.json` (id, name, version and `items`, the item ids in order)
and one `animations/<pack>/items/<id>.json` per item. The id of an item is its file name; a listed id
without a file, a file that is not listed and a duplicate id are errors. Each item has a `description`
that names the CapCut preset it recreates; it goes into the pack manifest, not into the item file.

## One item per pack

Every pack holds exactly one item, the same layout as GpufxVideoEditor-Assets. The sources stay grouped
in collections (one `pack.json`), and `scripts/item_packs.py` splits them:

| Field | Value |
|-------|-------|
| `id` | `<collection id>-<item id>`, for example `capcut-anim-basic-zoom-in` |
| `items` | the one item id, unchanged |
| `collection` | the collection id (the `pack.json` id), for example `capcut-anim-basic` |
| `collection_name` | the collection's display name (the `pack.json` name) |
| `name`, `description` | from the item |

Each pack zip has `manifest.json`, `items/<id>.json`, `LICENSE.txt` and `NOTICE.txt`. There are no
translations, so no `i18n/` folder. The pack zips are written to `<output>/clip-animation-packs/`, and
`<output>/clip-animation-packs.zip` is a plain zip (stored, flat) holding every zip of that folder; it is
the only file of a release.

Moves are in parts of the output frame. CapCut moves by a multiple of the clip size, so these packs
use a reference clip of 0.3 of the frame. Turns are in degrees, clockwise.

## Build

```sh
python scripts/pack.py           # dist/clip-animation-packs/*.zip and dist/clip-animation-packs.zip
python scripts/pack.py --check   # validate the sources only
```

Only the Python standard library is needed. The zips are reproducible byte for byte, and each
manifest and item is checked against the rules of the editor's strict pack reader (including the ease
forms `power`, `elastic`, `bounce`, `steps` and `wave` with their parameter ranges) before it is written.

## Install

Download `clip-animation-packs.zip` from the
[releases](https://github.com/tqk2811/GpufxVideoEditor-Assets-capcut/releases), unpack it and import each
inner zip in GpufxVideoEditor as a package. A tag `vX.Y.Z` builds and publishes the release.

## License

MIT, see [LICENSE](LICENSE).
