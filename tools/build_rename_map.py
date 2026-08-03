"""
Accumulate tools/rename_map.json from tools/pending_renames.json.

pending_renames.json is a list of {"owner","old","new"} entries authored by hand (owner is
"Stage" for globals, else the sprite name). This resolves each to its variable id using a
FRESH tools/var_index.json, and MERGES into the existing rename_map.json (keyed by id) so
earlier applied passes are preserved. Re-running is idempotent; already-applied names simply
don't re-resolve (they're kept via the existing map).

Workflow per pass:
  python tools/rename_vars.py --index > tools/var_index.json   # refresh
  # edit tools/pending_renames.json with the new (owner, old, new) entries
  python tools/build_rename_map.py
  python tools/rename_vars.py --map tools/rename_map.json --check
  python tools/rename_vars.py --map tools/rename_map.json --apply
"""
import json
import os

HERE = os.path.dirname(__file__)
IDX = os.path.join(HERE, 'var_index.json')
PENDING = os.path.join(HERE, 'pending_renames.json')
OUT = os.path.join(HERE, 'rename_map.json')


def load(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def main():
    idx = load(IDX, [])
    pending = load(PENDING, [])
    existing = {e['id']: e for e in load(OUT, [])}

    # (owner, current_name) -> id, for resolving pending entries
    by_owner_name = {}
    for d in idx:
        by_owner_name[(d['owner'], d['old'])] = d['id']

    added, skipped = 0, []
    for entry in pending:
        owner, old, new = entry['owner'], entry['old'], entry['new']
        if old == new:
            continue
        vid = by_owner_name.get((owner, old))
        if vid is None:
            # Either already renamed in a prior pass (kept via existing) or a typo.
            skipped.append((owner, old))
            continue
        existing[vid] = {'id': vid, 'owner': owner, 'old': old, 'new': new}
        added += 1

    out = list(existing.values())
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'rename_map.json now has {len(out)} entries (+{added} resolved this run)')
    if skipped:
        print(f'  {len(skipped)} pending not resolved (already applied or unknown):',
              skipped[:8], '...' if len(skipped) > 8 else '')


if __name__ == '__main__':
    main()
