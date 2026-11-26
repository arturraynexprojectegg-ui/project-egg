#!/usr/bin/env python3
"""python3 i18n/check_structure.py PE-01.05 — сверка структуры переводов с исходником."""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CYR_RU_ONLY = re.compile(r"[ыэъЫЭЪё]")


def shape(x):
    if isinstance(x, dict):
        return {k: shape(v) for k, v in x.items()}
    if isinstance(x, list):
        return [shape(v) for v in x]
    return type(x).__name__


def texts(x):
    if isinstance(x, dict):
        for v in x.values(): yield from texts(v)
    elif isinstance(x, list):
        for v in x: yield from texts(v)
    elif isinstance(x, str):
        yield x


ok = True
for code in sys.argv[1:]:
    for src, base in ((ROOT / "logobooks" / code / "data.json", "data"), (ROOT / "brandbooks" / code / "brand.json", "brand")):
        if not src.exists():
            continue
        s = json.loads(src.read_text())
        for lang in ("uk", "es"):
            f = src.with_name(f"{base}.{lang}.json")
            if not f.exists():
                print("НЕТ", f); ok = False; continue
            t = json.loads(f.read_text())
            if shape(s) != shape(t):
                print("СТРУКТУРА ОТЛИЧАЕТСЯ", f); ok = False
            bad = [x for x in texts(t) if CYR_RU_ONLY.search(x)]
            if lang == "es":
                bad = [x for x in texts(t) if re.search(r"[А-Яа-яІіЇїЄєҐґ]", x)]
            if bad:
                print("ОСТАЛСЯ ТЕКСТ НЕ НА ТОМ ЯЗЫКЕ", f, bad[:3]); ok = False
print("OK" if ok else "ЕСТЬ ОШИБКИ")
