#!/usr/bin/env python3
"""Build every clip animation pack of this repository into dist/<pack id>.zip.

    python scripts/pack.py              # -> dist/<pack id>.zip for each animations/<pack>/
    python scripts/pack.py -o out       # into out/
    python scripts/pack.py --check      # only validate the sources

Also packs every gpufx shader package of packages/gpufx/capcut-anim/<name>/ (manifest.json +
shaders/) into dist/<package id>.zip, with LICENSE.txt and NOTICE.txt added at the zip root. Each one
is checked first: id io.github.tqk2811.capcut-anim.<name>, the standard description, a float
`progress` param 0..1, and every shader it names present.

Source: animations/<pack>/pack.json (id, name, version, items). An item may carry a "description",
which stays in the source and is left out of the manifest. Each zip has, at its root, manifest.json
(format 1, type "clip-animation"), LICENSE.txt (the repository LICENSE) and NOTICE.txt. The zips are
reproducible byte for byte (sorted entries, fixed timestamps). Standard library only.

Before writing, each manifest is checked with the rules of the editor's strict reader
(crates/d3d12-backend/src/clip_animation_pack.rs and engine::check_curve of GpufxVideoEditor): known
fields only, safe ids, kinds in/out/loop, 0 < default_duration <= 60, applies_to kinds, curve tracks
with keyframes in rising t within 0..1 and finite values, known easings.
"""

import argparse
import json
import math
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANIMATIONS = ROOT / "animations"
SHADER_PACKAGES = ROOT / "packages" / "gpufx" / "capcut-anim"
SHADER_ID_PREFIX = "io.github.tqk2811.capcut-anim."
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")
KINDS = ("in", "out", "loop")
CLIP_KINDS = ("text", "image", "video", "sticker")
PROPERTIES = ("dx", "dy", "scale", "scaleX", "scaleY", "rotation", "opacity", "blur")
UNIT_EASES = ("linear", "hold", "easeIn", "easeOut", "easeInOut", "inCubic", "outCubic", "inSine",
              "outSine", "inOutSine", "outExpo", "elastic", "bounce")
MAX_DEFAULT_DURATION = 60.0


def fail(message):
    sys.exit(f"error: {message}")


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def check_fields(where, obj, required, optional=()):
    if not isinstance(obj, dict):
        fail(f"{where} is not an object")
    for name in required:
        if name not in obj:
            fail(f"{where} lacks '{name}'")
    for name in obj:
        if name not in required and name not in optional:
            fail(f"{where} has the unknown field '{name}'")


def check_ease(where, ease):
    if isinstance(ease, str):
        if ease not in UNIT_EASES:
            fail(f"{where}: unknown ease '{ease}'")
        return
    if not isinstance(ease, dict) or len(ease) != 1:
        fail(f"{where}: bad ease {ease!r}")
    name, value = next(iter(ease.items()))
    if name in ("backIn", "backOut"):
        check_fields(f"{where} {name}", value, ("amplitude",))
        if not finite(value["amplitude"]):
            fail(f"{where}: amplitude is not finite")
    elif name == "cubicBezier":
        if not (isinstance(value, list) and len(value) == 4 and all(finite(v) for v in value)):
            fail(f"{where}: cubicBezier needs 4 finite numbers")
    else:
        fail(f"{where}: unknown ease '{name}'")


def check_item(item):
    check_fields("an item", item, ("id", "name", "kind", "default_duration", "curve"), ("applies_to", "effect"))
    where = f"item '{item['id']}'"
    if not isinstance(item["id"], str) or not SAFE_ID.match(item["id"]) or item["id"] in (".", ".."):
        fail(f"{where}: unsafe id")
    if not isinstance(item["name"], str) or not item["name"].strip():
        fail(f"{where}: empty name")
    if item["kind"] not in KINDS:
        fail(f"{where}: kind '{item['kind']}' is not in, out or loop")
    duration = item["default_duration"]
    if not (finite(duration) and 0 < duration <= MAX_DEFAULT_DURATION):
        fail(f"{where}: default_duration must be in (0, {MAX_DEFAULT_DURATION}]")
    if "applies_to" in item:
        kinds = item["applies_to"]
        if not kinds or len(set(kinds)) != len(kinds) or any(k not in CLIP_KINDS for k in kinds):
            fail(f"{where}: bad applies_to")
    check_fields(f"{where} curve", item["curve"], ("tracks",))
    tracks = item["curve"]["tracks"]
    if not isinstance(tracks, dict) or not tracks:
        fail(f"{where}: the curve has no track")
    for prop, keys in tracks.items():
        if prop not in PROPERTIES:
            fail(f"{where}: unknown property '{prop}'")
        if not isinstance(keys, list) or not keys:
            fail(f"{where}: the {prop} track has no keyframe")
        last = 0.0
        for key in keys:
            check_fields(f"{where} {prop} keyframe", key, ("t", "value"), ("ease",))
            t = key["t"]
            if not (finite(t) and 0 <= t <= 1 and finite(key["value"])):
                fail(f"{where}: a {prop} keyframe is not finite or its t is not in 0..1")
            if t < last:
                fail(f"{where}: the {prop} keyframes are not in rising t")
            last = t
            if "ease" in key:
                check_ease(f"{where} {prop}", key["ease"])


def check_manifest(manifest):
    check_fields("the manifest", manifest, ("format", "type", "id", "name", "version", "license", "items"))
    if manifest["format"] != 1 or manifest["type"] != "clip-animation":
        fail("format must be 1 and type 'clip-animation'")
    if not SAFE_ID.match(manifest["id"]):
        fail("unsafe pack id")
    for name in ("name", "version"):
        if not manifest[name].strip():
            fail(f"empty {name}")
    check_fields("license", manifest["license"], ("spdx", "files"))
    if not manifest["license"]["spdx"].strip() or not manifest["license"]["files"]:
        fail("license.spdx and license.files must not be empty")
    items = manifest["items"]
    if not items:
        fail("items is empty")
    ids = [str(item.get("id", "")).lower() for item in items]
    if len(set(ids)) != len(ids):
        fail("an item id is used twice")
    for item in items:
        check_item(item)


NOTICE = """These clip animations are recreated and optimized with reference to CapCut's resources.
Only motion parameters (durations, easings, amplitudes, start and end values) were taken as
reference; the curves are written by hand as JSON. No CapCut asset, code, shader, font or image is
included. CapCut is a trademark of its owner; this project is not affiliated with it.
"""


def build_manifest(source_file):
    source = json.loads(source_file.read_text(encoding="utf-8"))
    check_fields(source_file.parent.name + "/pack.json", source, ("id", "name", "version", "items"))
    if source["id"] != source_file.parent.name:
        fail(f"{source_file.parent.name}: the pack id '{source['id']}' is not the folder name")
    items = []
    for item in source["items"]:
        if not isinstance(item, dict):
            fail(f"{source['id']}: an item is not an object")
        description = item.get("description")
        if not isinstance(description, str) or "Recreated and optimized with reference to CapCut's resources" not in description:
            fail(f"{source['id']}: item '{item.get('id')}' needs the description note")
        items.append({name: value for name, value in item.items() if name != "description"})
    return {
        "format": 1,
        "type": "clip-animation",
        "id": source["id"],
        "name": source["name"],
        "version": source["version"],
        "license": {"spdx": "MIT", "files": ["LICENSE.txt", "NOTICE.txt"]},
        "items": items,
    }


SHADER_NOTICE = """This gpufx package recreates the behaviour of a CapCut animation, written anew from a
description of how it looks. No CapCut asset, code, shader, font or image is included. CapCut is a
trademark of its owner; this project is not affiliated with it.
"""
SHADER_DESCRIPTION = re.compile(r'Recreation of the CapCut "[^"]+" animation\. Drive `progress` from 0 to 1\.')


def check_shader_package(folder):
    """The manifest follows this repository's rules and the package holds exactly its shaders."""
    where = f"packages/gpufx/capcut-anim/{folder.name}"
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("id") != SHADER_ID_PREFIX + folder.name:
        fail(f"{where}: the id must be {SHADER_ID_PREFIX + folder.name}")
    if not SHADER_DESCRIPTION.fullmatch(str(manifest.get("description", ""))):
        fail(f"{where}: the description does not follow the standard form")
    progress = [p for p in manifest.get("params", []) if p.get("name") == "progress"]
    if len(progress) != 1 or progress[0].get("type") != "float" or progress[0].get("min") != 0 \
            or progress[0].get("max") != 1:
        fail(f"{where}: needs one float param 'progress' from 0 to 1")
    names = {"manifest.json"}
    for group in manifest.get("groups", []):
        for step in group.get("passes", []):
            shader = step.get("shader", "")
            if not shader or not (folder / shader).is_file():
                fail(f"{where}: missing shader '{shader}'")
            names.add(shader)
    extra = {f.relative_to(folder).as_posix() for f in folder.rglob("*") if f.is_file()} - names
    if extra:
        fail(f"{where}: files no pass uses: {', '.join(sorted(extra))}")
    return manifest, sorted(names)


def write_zip(target, manifest=None, entries=None):
    if entries is None:
        entries = {
            "manifest.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            "NOTICE.txt": NOTICE,
        }
    entries["LICENSE.txt"] = (ROOT / "LICENSE").read_text(encoding="utf-8")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temporary, "w") as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.create_system = 3
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, entries[name].replace("\r\n", "\n").encode("utf-8"), compresslevel=9)
    temporary.replace(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-o", "--output", type=Path, default=ROOT / "dist", help="output directory")
    parser.add_argument("--check", action="store_true", help="only validate the source")
    args = parser.parse_args()
    sources = sorted(ANIMATIONS.glob("*/pack.json"))
    if not sources:
        fail("no animations/<pack>/pack.json found")
    for source_file in sources:
        manifest = build_manifest(source_file)
        check_manifest(manifest)
        if args.check:
            print(f"{manifest['id']}: {len(manifest['items'])} items ok")
            continue
        target = args.output / f"{manifest['id']}.zip"
        write_zip(target, manifest)
        print(f"wrote {target} ({len(manifest['items'])} items)")
    for folder in sorted(f for f in SHADER_PACKAGES.glob("*") if (f / "manifest.json").is_file()):
        manifest, names = check_shader_package(folder)
        if args.check:
            print(f"{manifest['id']}: ok")
            continue
        entries = {name: (folder / name).read_text(encoding="utf-8") for name in names}
        entries["NOTICE.txt"] = SHADER_NOTICE
        target = args.output / f"{manifest['id']}.zip"
        write_zip(target, entries=entries)
        print(f"wrote {target}")


if __name__ == "__main__":
    main()
