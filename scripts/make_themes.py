#!/usr/bin/env python3
"""Generate every theme from one palette definition.

Two layouts — noctu (two rows) and panel (three rows) — share a set of roles:
chip bodies, icon cells, per-meter bar/value pairs, timers, accents. A palette
names a handful of colours; the muted bars are derived by blending each accent
toward that theme's own background, so the design rules hold automatically.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
THEMES = os.path.join(ROOT, 'themes')


def mix(fg, bg, t):
    f = [int(fg[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(bg[i:i + 2], 16) for i in (0, 2, 4)]
    return ''.join('%02X' % round(f[i] * (1 - t) + b[i] * t) for i in range(3))


# role -> [(widget id, field)] per layout
COMMON = {
  'chip1_body':  [('l1-padl','backgroundColor'),('l1-padr','backgroundColor'),
                  ('l1-model','backgroundColor'),('l1-cap','color')],
  'chip1_icon':  [('l1-icon','backgroundColor')],
  'chip1_glyph': [('l1-icon','color')],
  'chip1_ink':   [('l1-model','color')],
  'chip2_body':  [('l2-padl','backgroundColor'),('l2-branch','backgroundColor'),('l2-cap','color')],
  'chip2_icon':  [('l2-icon','backgroundColor')],
  'chip2_glyph': [('l2-icon','color')],
  'chip2_ink':   [('l2-branch','color')],
  'ctx_bar':  [('l1-bar','color')],
  'ctx_val':  [('l1-pct','color'),('l1-lab','color')],
  'effort':   [('l1-effort','color')],
  'speed':    [('l1-speed','color')],
  'sep':      [('*separator*','color')],
}
NOCTU = dict(COMMON, **{
  'week_bar': [('l2-bar','color')],
  'week_val': [('l2-pct','color'),('l2-lab','color')],
  'week_timer':[('l2-reset','color')],
  'opus':     [('l2-opus','color')],
  'opuslab':  [('l2-opuslab','color')],
  'cost':     [('l2-cost','color')],
  'status':   [('l2-status','color')],
})
PANEL = dict(COMMON, **{
  'chip3_body': [('l3-padl','backgroundColor'),('l3-padr','backgroundColor'),
                 ('l3-label','backgroundColor'),('l3-cap','color')],
  'chip3_icon': [('l3-icon','backgroundColor')],
  'chip3_glyph':[('l3-icon','color')],
  'chip3_ink':  [('l3-label','color')],
  'ses_bar':  [('l2-bar','color')],
  'ses_val':  [('l2-pct','color'),('l2-lab','color')],
  'ses_timer':[('l2-reset','color')],
  'changes':  [('l2-changes','color')],
  'cost':     [('l2-cost','color')],
  'week_bar': [('l3-bar','color')],
  'week_val': [('l3-pct','color'),('l3-lab','color')],
  'week_timer':[('l3-reset','color')],
  'opus':     [('l3-opus','color')],
  'opuslab':  [('l3-opuslab','color')],
  'status':   [('l3-status','color')],
})


def colours(pal):
    bg, fg = pal['bg'], pal['fg']
    light = pal.get('light')
    bar_t, timer_t = (.32, .18) if light else (.62, .25)
    model, branch, limit = pal['model'], pal['branch'], pal['limit']
    return {
      'chip1_body': model, 'chip1_icon': mix(model, bg, .45), 'chip1_glyph': pal['glyph'], 'chip1_ink': bg,
      'chip2_body': branch,'chip2_icon': mix(branch, bg, .45),'chip2_glyph': pal['glyph'], 'chip2_ink': bg,
      'chip3_body': limit, 'chip3_icon': mix(limit, bg, .45), 'chip3_glyph': pal['glyph'], 'chip3_ink': bg,
      'ctx_bar':  mix(pal['ctx'], bg, bar_t),  'ctx_val':  pal['ctx'],
      'ses_bar':  mix(pal['ses'], bg, bar_t),  'ses_val':  pal['ses'],
      'week_bar': mix(pal['week'], bg, bar_t), 'week_val': pal['week'],
      'ses_timer': mix(pal['ses'], bg, timer_t), 'week_timer': mix(pal['week'], bg, timer_t),
      'effort': pal['green'], 'speed': pal['blue'], 'cost': pal['green'],
      'changes': pal['yellow'], 'status': pal['green'],
      'opus': pal['red'],
      'opuslab': mix(pal['red'], bg, .20 if light else .45),
      'sep': pal['sep'],
    }


def paint(template, roles, values):
    cfg = json.loads(json.dumps(template))
    for role, targets in roles.items():
        val = 'hex:' + values[role]
        for wid, field in targets:
            for line in cfg['lines']:
                for w in line:
                    if wid == '*separator*':
                        if w.get('type') == 'separator':
                            w[field] = val
                    elif w.get('id') == wid:
                        w[field] = val
    return cfg


PALETTES = {
 # Each palette leads with its own signature colour rather than all of them
 # defaulting to purple/green, or they end up indistinguishable.
 'nocturne': dict(bg='0B0E14', fg='C6CCDA', glyph='FFFFFF', model='7C5CFF', branch='2E9E7A',
    limit='B69CFF', ctx='F0C755', ses='E8903C', week='B69CFF', green='3E8E5A', blue='5B9BE8',
    yellow='E6B34A', red='FF6B6B', sep='79808E'),
 # Dracula leads pink
 'dracula': dict(bg='282A36', fg='F8F8F2', glyph='282A36', model='FF79C6', branch='50FA7B',
    limit='BD93F9', ctx='F1FA8C', ses='FFB86C', week='BD93F9', green='50FA7B', blue='8BE9FD',
    yellow='F1FA8C', red='FF5555', sep='6272A4'),
 # Tokyo Night leads blue
 'tokyo-night': dict(bg='1A1B26', fg='A9B1D6', glyph='1A1B26', model='7AA2F7', branch='9ECE6A',
    limit='BB9AF7', ctx='E0AF68', ses='FF9E64', week='BB9AF7', green='9ECE6A', blue='7DCFFF',
    yellow='E0AF68', red='F7768E', sep='565F89'),
 # Palenight leads cyan
 'palenight': dict(bg='292D3E', fg='A6ACCD', glyph='292D3E', model='89DDFF', branch='C3E88D',
    limit='C792EA', ctx='FFCB6B', ses='F78C6C', week='C792EA', green='C3E88D', blue='82AAFF',
    yellow='FFCB6B', red='F07178', sep='5C6685'),
 # Nord: cold, low chroma, no warm accents at all
 'nord': dict(bg='2E3440', fg='D8DEE9', glyph='2E3440', model='88C0D0', branch='A3BE8C',
    limit='B48EAD', ctx='EBCB8B', ses='D08770', week='B48EAD', green='A3BE8C', blue='81A1C1',
    yellow='EBCB8B', red='BF616A', sep='4C566A'),
 # Gruvbox: warm and earthy, the opposite end from Nord
 'gruvbox': dict(bg='282828', fg='EBDBB2', glyph='282828', model='D3869B', branch='B8BB26',
    limit='FE8019', ctx='FABD2F', ses='8EC07C', week='FE8019', green='B8BB26', blue='83A598',
    yellow='FABD2F', red='FB4934', sep='665C54'),
 # Material Light: the only light one
 'material-light': dict(bg='FAFAFA', fg='546E7A', glyph='FFFFFF', model='7C4DFF', branch='39ADB5',
    limit='6182B8', ctx='F6A434', ses='F76D47', week='6182B8', green='5B8C1F', blue='3E6AB8',
    yellow='B07000', red='E53935', sep='90A4AE', light=True),
}

if __name__ == '__main__':
    for layout, roles in (('noctu', NOCTU), ('panel', PANEL)):
        template = json.load(open(os.path.join(THEMES, layout, 'settings.json')))
        for name, pal in PALETTES.items():
            if name == 'nocturne':
                continue  # the template is already the nocturne palette
            out = os.path.join(THEMES, f'{layout}-{name}')
            os.makedirs(out, exist_ok=True)
            json.dump(paint(template, roles, colours(pal)),
                      open(os.path.join(out, 'settings.json'), 'w'), indent=2, ensure_ascii=False)
            print('built', f'{layout}-{name}')
