"""
Attach comments to custom-block definitions in project.json.

Reads tools/block_comments.json — a list of {"sprite","proccode","text"} — and, for each,
finds the matching custom block (procedures_prototype -> its procedures_definition parent)
and attaches a Scratch comment to that definition. Idempotent: if the definition already has
a comment linked (from a prior run), its text is updated instead of duplicated.

sb3 shape:
  target.comments[cid] = {blockId, x, y, width, height, minimized, text}
  and the definition block gets  block["comment"] = cid

Comments do not affect execution. Run:  python tools/add_comments.py [--apply]
Without --apply it reports what it would do.
"""
import argparse
import json
import os

HERE = os.path.dirname(__file__)
PROJECT = os.path.join(HERE, '..', 'extracted-sb3-file', 'project.json')
COMMENTS = os.path.join(HERE, 'block_comments.json')


def find_definition(target, proccode):
    """Return the block id of the procedures_definition for a proccode, or None."""
    blocks = target['blocks']
    for bid, b in blocks.items():
        if isinstance(b, dict) and b.get('opcode') == 'procedures_prototype':
            if b.get('mutation', {}).get('proccode') == proccode:
                # the prototype's parent is the procedures_definition hat
                return b.get('parent')
    return None


def next_comment_id(target, sprite):
    existing = target.setdefault('comments', {})
    n = 1
    while f'doc_{sprite}_{n}' in existing:
        n += 1
    return f'doc_{sprite}_{n}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    project = json.load(open(PROJECT, encoding='utf-8'))
    wanted = json.load(open(COMMENTS, encoding='utf-8'))
    by_name = {('Stage' if t.get('isStage') else t['name']): t for t in project['targets']}

    added, updated, missing = 0, 0, []
    for item in wanted:
        sprite, proccode, text = item['sprite'], item['proccode'], item['text']
        t = by_name.get(sprite)
        if not t:
            missing.append((sprite, proccode, 'no such sprite'))
            continue
        def_id = find_definition(t, proccode)
        if not def_id or def_id not in t['blocks']:
            missing.append((sprite, proccode, 'no custom block'))
            continue
        def_block = t['blocks'][def_id]
        comments = t.setdefault('comments', {})
        existing_cid = def_block.get('comment')
        if existing_cid and existing_cid in comments:
            comments[existing_cid]['text'] = text
            updated += 1
        else:
            cid = next_comment_id(t, sprite)
            x = def_block.get('x', 0)
            y = def_block.get('y', 0)
            comments[cid] = {
                'blockId': def_id,
                'x': x,
                'y': y - 160,
                'width': 360,
                'height': 140,
                'minimized': False,
                'text': text,
            }
            def_block['comment'] = cid
            added += 1

    print(f'comments: added={added} updated={updated} missing={len(missing)}')
    for m in missing:
        print('  MISSING:', m)

    if args.apply and not missing:
        json.dump(project, open(PROJECT, 'w', encoding='utf-8'), ensure_ascii=False)
        print('APPLIED -> project.json')
    elif args.apply and missing:
        print('REFUSING to apply: resolve missing proccodes first.')
    else:
        print('(dry run — no files written)')


if __name__ == '__main__':
    main()
