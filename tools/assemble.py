#!/usr/bin/env python3
"""Assembles brush_maps from the three plugins it bundles.

    python3 tools/assemble.py <valve220> <map_convert> <map_agent>

Each argument is a git checkout of that plugin. The code of the three is the source of truth: this
script copies their editor packages into this plugin, renames their packages and import paths to
brush_maps, joins the three root packages into one and gives their API methods the brush_maps
prefix. It writes editor/, examples/ and SOURCES.json with the commit of each source, and leaves
the rest of the repository (manifest, README, licenses, this script) alone.

A change to the code goes to the plugin it belongs to; then this script runs again and the result
is committed here.
"""

import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "brush_maps"

# The source plugins, and the subpackages of each editor/ with their new package names.
PLUGINS = {
    "valve220": {"mapfile": "brush_maps_mapfile", "loader": "brush_maps_loader"},
    "map_convert": {"formats": "brush_maps_formats"},
    "map_agent": {"agent": "brush_maps_agent"},
}
SUBPACKAGE_OF = {"mapfile": "valve220", "loader": "valve220", "formats": "map_convert", "agent": "map_agent"}
OLD_PACKAGES = {
    "valve220_mapfile": "brush_maps_mapfile",
    "valve220_loader": "brush_maps_loader",
    "map_convert_formats": "brush_maps_formats",
    "map_agent_tools": "brush_maps_agent",
    "valve220_editor": "brush_maps_editor",
    "map_convert_editor": "brush_maps_editor",
    "map_agent_editor": "brush_maps_editor",
}
# The API methods, by their old name.
METHODS = ["map_convert.to_valve220", "map_convert.unpack_wad", "map_agent.layout", "map_agent.check"]


def fail(message):
    print(f"assemble: {message}", file=sys.stderr)
    sys.exit(1)


def commit_of(checkout):
    out = subprocess.run(["git", "-C", checkout, "rev-parse", "HEAD"], capture_output=True, text=True)
    if out.returncode != 0:
        fail(f"{checkout} is not a git checkout")
    dirty = subprocess.run(["git", "-C", checkout, "status", "--porcelain"], capture_output=True, text=True)
    if dirty.stdout.strip():
        fail(f"{checkout} has changes without a commit; commit them in that plugin first")
    return out.stdout.strip()


def rewrite(text, root):
    """The source of one file, as a file of brush_maps. root: the file is in a root package."""
    # Import paths of the subpackages.
    for sub, plugin in SUBPACKAGE_OF.items():
        text = text.replace(f'"project:plugins/{plugin}/editor/{sub}"', f'"project:plugins/{NAME}/editor/{sub}"')
    # The root packages become one: their imports of each other go, and so do their qualifiers.
    joined = []
    for plugin in PLUGINS:
        pattern = re.compile(r'^import\s+(\w+)\s+"project:plugins/' + plugin + r'/editor"\s*\n', re.M)
        for alias in pattern.findall(text):
            joined.append(alias)
        text = pattern.sub("", text)
    for method in METHODS:
        text = text.replace(method, NAME + "." + method.split(".", 1)[1])
    for alias in joined:
        if not root:
            fail(f"a subpackage imports the root package as {alias}")
        text = re.sub(r"(?<![\w.\"/-])" + alias + r"\.(?=[A-Za-z_])", "", text)
    for old, new in OLD_PACKAGES.items():
        text = re.sub(r"^package " + old + r"\b", "package " + new, text, flags=re.M)
    text = text.replace("which TrenchBroom edits and valve220 imports", f"which TrenchBroom edits and {NAME} imports")
    text = text.replace("where valve220 finds the textures", f"where {NAME} finds the textures")
    return text


def copy_tree(source, target, root):
    for entry in sorted(os.listdir(source)):
        path = os.path.join(source, entry)
        if os.path.isdir(path):
            continue
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        if entry.endswith(".odin"):
            text = rewrite(text, root)
        out = os.path.join(target, entry)
        if os.path.exists(out):
            fail(f"two sources write {os.path.relpath(out, HERE)}")
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(text)


def main():
    if len(sys.argv) != 4:
        fail("usage: assemble.py <valve220> <map_convert> <map_agent>")
    sources = dict(zip(PLUGINS, sys.argv[1:]))
    commits = {}
    for plugin, checkout in sources.items():
        with open(os.path.join(checkout, "plugin.mirai"), encoding="utf-8") as f:
            if json.load(f)["name"] != plugin:
                fail(f"{checkout} is not the plugin {plugin}")
        commits[plugin] = commit_of(checkout)

    editor = os.path.join(HERE, "editor")
    examples = os.path.join(HERE, "examples")
    for folder in (editor, examples):
        if os.path.isdir(folder):
            shutil.rmtree(folder)
    os.makedirs(editor)
    for plugin, subpackages in PLUGINS.items():
        source_editor = os.path.join(sources[plugin], "editor")
        copy_tree(source_editor, editor, root=True)
        for sub in subpackages:
            target = os.path.join(editor, sub)
            os.makedirs(target)
            copy_tree(os.path.join(source_editor, sub), target, root=False)
        source_examples = os.path.join(sources[plugin], "examples")
        if os.path.isdir(source_examples):
            shutil.copytree(source_examples, examples, dirs_exist_ok=False)
    # The examples name the methods as the plugin that has them.
    for folder, _, files in os.walk(examples):
        for entry in files:
            if not entry.endswith(".md"):
                continue
            path = os.path.join(folder, entry)
            with open(path, encoding="utf-8", newline="") as f:
                text = f.read()
            for method in METHODS:
                text = text.replace(method, NAME + "." + method.split(".", 1)[1])
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(text)

    repos = {"valve220": "mirai-valve220", "map_convert": "mirai-map-convert", "map_agent": "mirai-map-agent"}
    record = {plugin: {"url": f"https://github.com/5hif7y/{repos[plugin]}.git", "commit": commits[plugin]} for plugin in PLUGINS}
    with open(os.path.join(HERE, "SOURCES.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    for plugin, commit in commits.items():
        print(f"{plugin} {commit[:7]}")


if __name__ == "__main__":
    main()
