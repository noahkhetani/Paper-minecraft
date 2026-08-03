"""
Target-scoped variable/list renamer for the Scratch project.json.

Scratch binds variables/lists by **id**, with the name duplicated at every reference:
  - declaration:        target.variables[id] = [name, value]   /  target.lists[id] = [name, [items]]
  - block field:        block.fields.VARIABLE = [name, id]      (also LIST)
  - input primitive:    [12, name, id]  (variable reporter)     /  [13, name, id]  (list)
  - monitor:            {id, opcode, params:{VARIABLE|LIST: name}, spriteName}

CRUCIAL: ids are unique only **within a target**, not globally — the same id can name a
Stage global in one scope and a sprite-local in another, and a sprite-local shadows a global
of the same id. So a variable is identified by **(owner, id)**, and references resolve to the
local if the referencing target declares that id, else to the Stage global. This tool renames
strictly by (owner, id), updating only the references that actually resolve to that variable.

Custom-block *parameters* (argument_reporter_* / mutation argumentnames) are a different
namespace and are deliberately NOT touched.

Map file format: a JSON list of {"id","owner","old","new"} (owner = "Stage" for globals,
else the sprite name). Modes: --index | --map FILE (--check | --apply).
"""
import argparse
import json
import os
import sys
from collections import defaultdict


DEFAULT_PROJECT = os.path.join(
    os.path.dirname(__file__), '..', 'extracted-sb3-file', 'project.json'
)


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def target_name(t):
    return 'Stage' if t.get('isStage') else t['name']


def collect_declarations(project):
    """List every declaration as {id,kind,owner,scope,old}. Not keyed by id (ids repeat)."""
    out = []
    for t in project['targets']:
        owner = target_name(t)
        scope = 'global' if t.get('isStage') else 'local'
        for vid, d in t.get('variables', {}).items():
            out.append({'id': vid, 'kind': 'var', 'owner': owner, 'scope': scope, 'old': d[0]})
        for lid, d in t.get('lists', {}).items():
            out.append({'id': lid, 'kind': 'list', 'owner': owner, 'scope': scope, 'old': d[0]})
    return out


def local_ids_by_target(project):
    """sprite name -> set of ids it declares locally (used for shadow resolution)."""
    out = {}
    for t in project['targets']:
        if t.get('isStage'):
            continue
        out[t['name']] = set(t.get('variables', {})) | set(t.get('lists', {}))
    return out


def resolve_owner(ref_target, vid, local_ids):
    """Which variable does a reference to `vid` inside `ref_target` point to?
    The local if that target declares the id, otherwise the Stage global."""
    if ref_target != 'Stage' and vid in local_ids.get(ref_target, ()):
        return ref_target
    return 'Stage'


def load_map(path):
    """Return {(owner, id): new_name} from the map file."""
    mapping = {}
    for e in load(path):
        if e.get('id') and e.get('new') and e.get('owner'):
            mapping[(e['owner'], e['id'])] = e['new']
    return mapping


def apply_mapping(project, mapping):
    """Rename strictly by (owner, id). Returns counts per location type."""
    counts = {'decls': 0, 'fields': 0, 'inputs': 0, 'monitors': 0}
    by_name = {target_name(t): t for t in project['targets']}
    local_ids = local_ids_by_target(project)

    # 1. declarations — only in the owning target
    for (owner, vid), new in mapping.items():
        t = by_name.get(owner)
        if not t:
            continue
        if vid in t.get('variables', {}):
            t['variables'][vid][0] = new
            counts['decls'] += 1
        elif vid in t.get('lists', {}):
            t['lists'][vid][0] = new
            counts['decls'] += 1

    # 2. block references — rename only refs that resolve to a mapped (owner, id)
    for t in project['targets']:
        tname = target_name(t)
        for b in t.get('blocks', {}).values():
            if not isinstance(b, dict):
                continue
            fields = b.get('fields', {})
            for key in ('VARIABLE', 'LIST'):
                ref = fields.get(key)
                if isinstance(ref, list) and len(ref) >= 2:
                    new = mapping.get((resolve_owner(tname, ref[1], local_ids), ref[1]))
                    if new is not None:
                        ref[0] = new
                        counts['fields'] += 1
            for inp in (b.get('inputs', {}) or {}).values():
                if not isinstance(inp, list):
                    continue
                for el in inp:
                    if isinstance(el, list) and len(el) >= 3 and el[0] in (12, 13):
                        new = mapping.get((resolve_owner(tname, el[2], local_ids), el[2]))
                        if new is not None:
                            el[1] = new
                            counts['inputs'] += 1

    # 3. monitors — global monitors have spriteName null; sprite monitors carry the name
    for m in project.get('monitors', []):
        owner = m.get('spriteName') or 'Stage'
        new = mapping.get((owner, m.get('id')))
        if new is not None:
            params = m.get('params', {})
            for key in ('VARIABLE', 'LIST'):
                if key in params:
                    params[key] = new
                    counts['monitors'] += 1
    return counts


def collisions(project):
    """Set of (target, name) where two DISTINCT variables (by (owner,id)) share a name in a
    target's visible namespace (its locals + the non-shadowed globals)."""
    stage = next(t for t in project['targets'] if t.get('isStage'))
    global_decls = []  # (id, name)
    for vid, d in stage.get('variables', {}).items():
        global_decls.append((vid, d[0]))
    for lid, d in stage.get('lists', {}).items():
        global_decls.append((lid, d[0]))

    found = set()
    for t in project['targets']:
        tname = target_name(t)
        local_ids = set(t.get('variables', {})) | set(t.get('lists', {}))
        seen = {}  # name -> identity (owner, id)
        # visible globals (skip ids shadowed by a local of this target)
        if not t.get('isStage'):
            for vid, name in global_decls:
                if vid not in local_ids:
                    seen[name] = ('Stage', vid)
        # locals (or, for Stage, its own decls)
        decls = list(t.get('variables', {}).items()) + list(t.get('lists', {}).items())
        for vid, d in decls:
            name = d[0]
            ident = (tname, vid)
            if name in seen and seen[name] != ident:
                found.add((tname, name))
            else:
                seen[name] = ident
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', default=DEFAULT_PROJECT)
    ap.add_argument('--out', dest='out', default=None)
    ap.add_argument('--map', dest='map')
    ap.add_argument('--index', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    project = load(args.inp)

    if args.index:
        json.dump(collect_declarations(project), sys.stdout, ensure_ascii=False, indent=1)
        return

    if not args.map:
        ap.error('provide --map (with --check or --apply) or --index')

    mapping = load_map(args.map)
    by_name = {target_name(t): t for t in project['targets']}
    unknown = [
        (owner, vid) for (owner, vid) in mapping
        if owner not in by_name
        or (vid not in by_name[owner].get('variables', {})
            and vid not in by_name[owner].get('lists', {}))
    ]
    print(f'map entries: {len(mapping)}  unresolved (owner,id): {len(unknown)}')
    if unknown:
        print('  WARNING unresolved:', unknown[:8], '...' if len(unknown) > 8 else '')

    pre = collisions(project)
    counts = apply_mapping(project, mapping)
    post = collisions(project)
    introduced = post - pre

    print(f'rewrites: decls={counts["decls"]} fields={counts["fields"]} '
          f'inputs={counts["inputs"]} monitors={counts["monitors"]}')
    print(f'collisions: pre-existing={len(pre)} introduced={len(introduced)} '
          f'fixed-by-rename={len(pre - post)}')
    if introduced:
        print('  NEW collisions (must fix):')
        for owner, name in sorted(introduced)[:25]:
            print(f'    [{owner}] {name!r}')

    if args.apply:
        if introduced:
            print('REFUSING to apply: the mapping introduces new name collisions.')
            sys.exit(1)
        out_path = args.out or args.inp
        if out_path == args.inp and not os.path.exists(args.inp + '.bak'):
            with open(args.inp + '.bak', 'w', encoding='utf-8') as f:
                json.dump(load(args.inp), f, ensure_ascii=False)
            print(f'backed up original -> {args.inp}.bak')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(project, f, ensure_ascii=False)
        print(f'APPLIED -> {out_path}')
    else:
        print('(check only — no files written)')


if __name__ == '__main__':
    main()
