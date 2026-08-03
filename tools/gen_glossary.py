"""
Regenerate docs/variable-glossary.md from tools/rename_map.json so the glossary always
matches the applied renames. Groups by owner (Stage globals first, then sprites).
Run after each rename pass:  python tools/gen_glossary.py
"""
import json
import os

HERE = os.path.dirname(__file__)
MAP = os.path.join(HERE, 'rename_map.json')
OUT = os.path.join(HERE, '..', 'docs', 'variable-glossary.md')

INTRO = """# Variable glossary (renames)

Maps the original cryptic Scratch names to the readable names now in
`extracted-sb3-file/project.json`. Renames are applied strictly by **(owner, id)** with
`tools/rename_vars.py`, so behaviour is unchanged — only readability. This file is generated
from `tools/rename_map.json` by `tools/gen_glossary.py`; don't edit it by hand.

Conventions: the original used a leading `_` to mark engine-internal state; new names are
plain readable camelCase. Already-clear names (e.g. `Hardcore`, `XP_LEVEL`, `Beacon`) and
conventional loop counters (`i`, `x`, `y`, `t`) are intentionally left unchanged.

"""


def main():
    entries = json.load(open(MAP, encoding='utf-8'))
    by_owner = {}
    for e in entries:
        by_owner.setdefault(e.get('owner', 'Stage'), []).append(e)

    lines = [INTRO]
    total = len(entries)
    lines.append(f'**{total} names renamed so far**, across {len(by_owner)} target(s).\n')

    # Stage first, then sprites alphabetically
    order = ['Stage'] + sorted(o for o in by_owner if o != 'Stage')
    label = {'Stage': 'Stage (global state)'}
    for owner in order:
        rows = sorted(by_owner[owner], key=lambda e: e['new'])
        lines.append(f'\n## {label.get(owner, owner)} — {len(rows)} renamed\n')
        lines.append('| old | new |')
        lines.append('|-----|-----|')
        for e in rows:
            lines.append(f"| `{e['old']}` | `{e['new']}` |")

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'wrote {OUT} ({total} entries, {len(by_owner)} owners)')


if __name__ == '__main__':
    main()
