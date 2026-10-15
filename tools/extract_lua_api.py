#!/usr/bin/env python3
"""Recover Aspire's Lua (luabind) class/method names from `strings` output.

luabind registers methods in order, followed by the class name, so within a
run of identifier strings the class name terminates the run of its methods.
Known class names (taken from shipped gadget Lua) split runs where a class
follows another without noise between them.

Usage: extract_lua_api.py strings.txt gadgets_dir out.json
Output is a HEURISTIC catalog: verify against runtime before trusting.
"""
import json
import re
import sys
from pathlib import Path

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{1,63}$")
CTOR = re.compile(r"(?<![:.\w])([A-Z][A-Za-z0-9]+)\s*\(")
DEFN = re.compile(r"function\s+(?:[\w.:]*[.:])?([A-Za-z_]\w*)")


def known_classes(gadget_dirs):
    names, defined = set(), set()
    for root in gadget_dirs:
        for p in Path(root).rglob("*.lua"):
            text = p.read_text(errors="ignore")
            names.update(CTOR.findall(text))
            defined.update(DEFN.findall(text))
    return names - defined


def main(strings_path, gadgets, out):
    lines = Path(strings_path).read_text(errors="ignore").splitlines()
    known = known_classes(gadgets.split(":"))
    catalog, run = {}, []
    # region bounded around the binding table; found empirically
    start = next(i for i, l in enumerate(lines) if l == "ExportSelectionToSvg") - 6000
    end = start + 12000

    def flush():
        nonlocal run
        if len(run) >= 2:
            catalog.setdefault(run[-1], sorted(set(run[:-1])))
        run = []

    for line in lines[max(start, 0):end]:
        if IDENT.match(line) and not line.startswith(("At3d", "tri", "mc")):
            run.append(line)
            if line in known and len(run) > 1:
                flush()
        else:
            flush()
    flush()
    Path(out).write_text(json.dumps(
        {"source": "Aspire.exe strings (heuristic)", "classes": catalog},
        indent=1, sort_keys=True))
    print(f"{len(catalog)} classes -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
