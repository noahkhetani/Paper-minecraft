"""Lightweight Scratch block -> pseudocode decompiler.

Usage:
  python decompile.py <SpriteName>                  # list scripts + custom blocks
  python decompile.py <SpriteName> "<proccode>"     # one custom block definition
  python decompile.py <SpriteName> --hat <broadcast> # a 'when I receive' script
  python decompile.py <SpriteName> --grep <text>     # custom blocks whose code matches
"""
import json, os, sys, re

# Windows consoles default to cp1252; costume names contain unicode symbols.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SRC = os.path.join(os.path.dirname(__file__), '..', 'extracted-sb3-file', 'project.json')
with open(SRC, 'r', encoding='utf-8') as f:
    P = json.load(f)
TByName = {t['name']: t for t in P['targets']}


def blocks_of(t):
    return t['blocks']


def prim(v):
    """Render a primitive input array [type, value, ...]."""
    typ = v[0]
    if typ in (4, 5, 6, 7, 8):       # number kinds
        return str(v[1])
    if typ == 9:                      # color
        return f'#{v[1]}'
    if typ == 10:                     # string
        return json.dumps(v[1], ensure_ascii=False)
    if typ == 11:                     # broadcast
        return f'broadcast({v[1]!r})'
    if typ == 12:                     # variable
        return f'${v[1]}'
    if typ == 13:                     # list
        return f'@{v[1]}'
    return repr(v)


def render_input(blocks, inp):
    """inp = [shadowFlag, value, (shadowPrimitive)]"""
    if inp is None:
        return '_'
    val = inp[1] if len(inp) > 1 else None
    if val is None:
        return '_'
    if isinstance(val, list):
        return prim(val)
    if isinstance(val, str):           # block id -> reporter
        return render_reporter(blocks, val)
    return repr(val)


def field(b, name):
    f = b.get('fields', {}).get(name)
    return f[0] if f else '?'


def args(blocks, b, *names):
    return [render_input(blocks, b.get('inputs', {}).get(n)) for n in names]


REPORTERS = {
    'operator_add': lambda B, b: f'({I(B,b,"NUM1")} + {I(B,b,"NUM2")})',
    'operator_subtract': lambda B, b: f'({I(B,b,"NUM1")} - {I(B,b,"NUM2")})',
    'operator_multiply': lambda B, b: f'({I(B,b,"NUM1")} * {I(B,b,"NUM2")})',
    'operator_divide': lambda B, b: f'({I(B,b,"NUM1")} / {I(B,b,"NUM2")})',
    'operator_mod': lambda B, b: f'({I(B,b,"NUM1")} mod {I(B,b,"NUM2")})',
    'operator_random': lambda B, b: f'random({I(B,b,"FROM")}, {I(B,b,"TO")})',
    'operator_lt': lambda B, b: f'({I(B,b,"OPERAND1")} < {I(B,b,"OPERAND2")})',
    'operator_gt': lambda B, b: f'({I(B,b,"OPERAND1")} > {I(B,b,"OPERAND2")})',
    'operator_equals': lambda B, b: f'({I(B,b,"OPERAND1")} == {I(B,b,"OPERAND2")})',
    'operator_and': lambda B, b: f'({I(B,b,"OPERAND1")} and {I(B,b,"OPERAND2")})',
    'operator_or': lambda B, b: f'({I(B,b,"OPERAND1")} or {I(B,b,"OPERAND2")})',
    'operator_not': lambda B, b: f'(not {I(B,b,"OPERAND")})',
    'operator_join': lambda B, b: f'join({I(B,b,"STRING1")}, {I(B,b,"STRING2")})',
    'operator_letter_of': lambda B, b: f'letter({I(B,b,"LETTER")}, {I(B,b,"STRING")})',
    'operator_length': lambda B, b: f'len({I(B,b,"STRING")})',
    'operator_contains': lambda B, b: f'contains({I(B,b,"STRING1")}, {I(B,b,"STRING2")})',
    'operator_mathop': lambda B, b: f'{field(b,"OPERATOR")}({I(B,b,"NUM")})',
    'operator_round': lambda B, b: f'round({I(B,b,"NUM")})',
    'data_itemoflist': lambda B, b: f'@{field(b,"LIST")}[{I(B,b,"INDEX")}]',
    'data_itemnumoflist': lambda B, b: f'indexOf(@{field(b,"LIST")}, {I(B,b,"ITEM")})',
    'data_lengthoflist': lambda B, b: f'len(@{field(b,"LIST")})',
    'data_listcontainsitem': lambda B, b: f'@{field(b,"LIST")}.contains({I(B,b,"ITEM")})',
    'data_variable': lambda B, b: f'${field(b,"VARIABLE")}',
    'data_listcontents': lambda B, b: f'@{field(b,"LIST")}',
    'argument_reporter_string_number': lambda B, b: f'%{field(b,"VALUE")}',
    'argument_reporter_boolean': lambda B, b: f'%{field(b,"VALUE")}',
    'sensing_mousex': lambda B, b: 'mouseX',
    'sensing_mousey': lambda B, b: 'mouseY',
    'sensing_timer': lambda B, b: 'timer',
    'looks_costumenumbername': lambda B, b: f'costume.{field(b,"NUMBER_NAME")}',
    'sensing_keypressed': lambda B, b: f'keyDown({I(B,b,"KEY_OPTION")})',
    'sensing_of': lambda B, b: f'{field(b,"PROPERTY")} of {I(B,b,"OBJECT")}',
}


def I(B, b, name):
    return render_input(B, b.get('inputs', {}).get(name))


def render_reporter(blocks, bid):
    b = blocks.get(bid)
    if not isinstance(b, dict):
        return '?'
    op = b['opcode']
    if op in REPORTERS:
        return REPORTERS[op](blocks, b)
    if op == 'procedures_call':
        return f'CALL[{b["mutation"]["proccode"]}]({", ".join(call_args(blocks,b))})'
    # generic reporter
    ins = ', '.join(f'{k}={render_input(blocks,v)}' for k, v in b.get('inputs', {}).items())
    fs = ', '.join(f'{k}={v[0]}' for k, v in b.get('fields', {}).items())
    inner = ', '.join(x for x in (ins, fs) if x)
    return f'{op}({inner})'


def call_args(blocks, b):
    mut = b['mutation']
    argids = json.loads(mut.get('argumentids', '[]'))
    out = []
    for aid in argids:
        out.append(render_input(blocks, b.get('inputs', {}).get(aid)))
    return out


def render_stack(blocks, bid, indent):
    out = []
    pad = '  ' * indent
    while bid:
        b = blocks.get(bid)
        if not isinstance(b, dict):
            break
        op = b['opcode']
        line = render_statement(blocks, b, indent)
        if line is not None:
            out.append(line)
        bid = b.get('next')
    return out


def render_statement(blocks, b, indent):
    pad = '  ' * indent
    op = b['opcode']
    if op == 'control_if':
        head = f'{pad}if {I(blocks,b,"CONDITION")}:'
        body = render_substack(blocks, b, 'SUBSTACK', indent + 1)
        return '\n'.join([head, *body])
    if op == 'control_if_else':
        head = f'{pad}if {I(blocks,b,"CONDITION")}:'
        b1 = render_substack(blocks, b, 'SUBSTACK', indent + 1)
        b2 = render_substack(blocks, b, 'SUBSTACK2', indent + 1)
        return '\n'.join([head, *b1, f'{pad}else:', *b2])
    if op in ('control_repeat',):
        head = f'{pad}repeat {I(blocks,b,"TIMES")}:'
        body = render_substack(blocks, b, 'SUBSTACK', indent + 1)
        return '\n'.join([head, *body])
    if op == 'control_repeat_until':
        head = f'{pad}until {I(blocks,b,"CONDITION")}:'
        body = render_substack(blocks, b, 'SUBSTACK', indent + 1)
        return '\n'.join([head, *body])
    if op == 'control_forever':
        head = f'{pad}forever:'
        body = render_substack(blocks, b, 'SUBSTACK', indent + 1)
        return '\n'.join([head, *body])
    if op == 'control_while':
        head = f'{pad}while {I(blocks,b,"CONDITION")}:'
        body = render_substack(blocks, b, 'SUBSTACK', indent + 1)
        return '\n'.join([head, *body])
    if op == 'data_setvariableto':
        return f'{pad}${field(b,"VARIABLE")} = {I(blocks,b,"VALUE")}'
    if op == 'data_changevariableby':
        return f'{pad}${field(b,"VARIABLE")} += {I(blocks,b,"VALUE")}'
    if op == 'data_addtolist':
        return f'{pad}@{field(b,"LIST")}.add({I(blocks,b,"ITEM")})'
    if op == 'data_deleteoflist':
        return f'{pad}@{field(b,"LIST")}.delete({I(blocks,b,"INDEX")})'
    if op == 'data_deletealloflist':
        return f'{pad}@{field(b,"LIST")}.clear()'
    if op == 'data_insertatlist':
        return f'{pad}@{field(b,"LIST")}.insert({I(blocks,b,"INDEX")}, {I(blocks,b,"ITEM")})'
    if op == 'data_replaceitemoflist':
        return f'{pad}@{field(b,"LIST")}[{I(blocks,b,"INDEX")}] = {I(blocks,b,"ITEM")}'
    if op == 'procedures_call':
        return f'{pad}CALL[{b["mutation"]["proccode"]}]({", ".join(call_args(blocks,b))})'
    if op == 'control_stop':
        return f'{pad}stop({field(b,"STOP_OPTION")})'
    if op == 'event_broadcast':
        return f'{pad}broadcast({I(blocks,b,"BROADCAST_INPUT")})'
    if op == 'event_broadcastandwait':
        return f'{pad}broadcastAndWait({I(blocks,b,"BROADCAST_INPUT")})'
    if op == 'control_wait':
        return f'{pad}wait {I(blocks,b,"DURATION")}s'
    if op == 'control_create_clone_of':
        return f'{pad}createCloneOf({I(blocks,b,"CLONE_OPTION")})'
    if op == 'control_delete_this_clone':
        return f'{pad}deleteThisClone()'
    # generic statement
    ins = ', '.join(f'{k}={render_input(blocks,v)}' for k, v in b.get('inputs', {}).items())
    fs = ', '.join(f'{k}={v[0]}' for k, v in b.get('fields', {}).items())
    inner = ', '.join(x for x in (ins, fs) if x)
    return f'{pad}{op}({inner})'


def render_substack(blocks, b, name, indent):
    inp = b.get('inputs', {}).get(name)
    if not inp:
        return []
    sub = inp[1]
    if isinstance(sub, str):
        return render_stack(blocks, sub, indent)
    return []


def find_proc_def(blocks, proccode):
    for bid, b in blocks.items():
        if isinstance(b, dict) and b.get('opcode') == 'procedures_prototype':
            if b['mutation']['proccode'] == proccode:
                # the definition hat is its parent
                return b.get('parent')
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    sprite = sys.argv[1]
    t = TByName.get(sprite)
    if not t:
        print('No such sprite. Available:', ', '.join(TByName))
        return
    B = blocks_of(t)

    if len(sys.argv) == 2:
        protos = [b['mutation']['proccode'] for b in B.values()
                  if isinstance(b, dict) and b.get('opcode') == 'procedures_prototype']
        print(f'{sprite}: {len(protos)} custom blocks')
        for pc in sorted(protos):
            print('  ', pc)
        return

    if sys.argv[2] == '--grep':
        needle = sys.argv[3].lower()
        for b in B.values():
            if isinstance(b, dict) and b.get('opcode') == 'procedures_prototype':
                if needle in b['mutation']['proccode'].lower():
                    print('  ', b['mutation']['proccode'])
        return

    if sys.argv[2] == '--hat':
        name = sys.argv[3]
        for bid, b in B.items():
            if isinstance(b, dict) and b.get('opcode') == 'event_whenbroadcastreceived':
                if field(b, 'BROADCAST_OPTION') == name:
                    print(f'when I receive "{name}":')
                    print('\n'.join(render_stack(B, b.get('next'), 1)))
                    print()
        return

    if sys.argv[2] == '--clone':
        for bid, b in B.items():
            if isinstance(b, dict) and b.get('opcode') == 'control_start_as_clone':
                print('when I start as a clone:')
                print('\n'.join(render_stack(B, b.get('next'), 1)))
                print()
        return

    if sys.argv[2] == '--flag':
        for bid, b in B.items():
            if isinstance(b, dict) and b.get('opcode') == 'event_whenflagclicked':
                print('when green flag clicked:')
                print('\n'.join(render_stack(B, b.get('next'), 1)))
                print()
        return

    if sys.argv[2] == '--hats':
        for bid, b in B.items():
            if not isinstance(b, dict):
                continue
            op = b.get('opcode')
            if op == 'event_whenbroadcastreceived':
                print('broadcast:', field(b, 'BROADCAST_OPTION'))
            elif op in ('control_start_as_clone', 'event_whenflagclicked',
                        'event_whenkeypressed', 'event_whenthisspriteclicked',
                        'event_whenbackdropswitchesto'):
                extra = ''
                if op == 'event_whenkeypressed':
                    extra = ' key=' + field(b, 'KEY_OPTION')
                print(op.replace('event_when', '').replace('control_', '') + extra)
        return

    proccode = sys.argv[2]
    defid = find_proc_def(B, proccode)
    if not defid:
        print('No custom block:', proccode)
        return
    defb = B[defid]
    print(f'define {proccode}:')
    print('\n'.join(render_stack(B, defb.get('next'), 1)))


if __name__ == '__main__':
    main()
