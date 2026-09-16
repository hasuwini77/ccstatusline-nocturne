import json, copy, os

LIVE = '/home/hasuwini77/.config/ccstatusline/settings.json'
OUT = '/home/hasuwini77/dev/ccstatusline-nocturne/themes'

def mix(fg, bg, t):
    """blend fg toward bg by t (0..1) — used to derive muted bars and icon cells"""
    f = [int(fg[i:i+2], 16) for i in (0, 2, 4)]
    b = [int(bg[i:i+2], 16) for i in (0, 2, 4)]
    return ''.join('%02X' % round(f[i] * (1 - t) + b[i] * t) for i in range(3))

# role -> (widget id, field)
ROLES = {
  'chip1_body':   [('l1-padl','backgroundColor'),('l1-padr','backgroundColor'),('l1-model','backgroundColor'),('l1-cap','color')],
  'chip1_icon':   [('l1-icon','backgroundColor')],
  'chip1_glyph':  [('l1-icon','color')],
  'chip1_ink':    [('l1-model','color')],
  'chip2_body':   [('l2-padl','backgroundColor'),('l2-branch','backgroundColor'),('l2-cap','color')],
  'chip2_icon':   [('l2-icon','backgroundColor')],
  'chip2_glyph':  [('l2-icon','color')],
  'chip2_ink':    [('l2-branch','color')],
  'chip3_body':   [('l3-padl','backgroundColor'),('l3-padr','backgroundColor'),('l3-label','backgroundColor'),('l3-cap','color')],
  'chip3_icon':   [('l3-icon','backgroundColor')],
  'chip3_glyph':  [('l3-icon','color')],
  'chip3_ink':    [('l3-label','color')],
  'm1_bar':  [('l1-bar','color')],  'm1_val': [('l1-pct','color'),('l1-lab','color')],
  'm2_bar':  [('l2-bar','color')],  'm2_val': [('l2-pct','color'),('l2-lab','color')],
  'm3_bar':  [('l3-bar','color')],  'm3_val': [('l3-pct','color'),('l3-lab','color')],
  'timer2':  [('l2-reset','color')], 'timer3': [('l3-reset','color')],
  'effort':  [('l1-effort','color')], 'speed': [('l1-speed','color')],
  'cost':    [('l2-cost','color')],  'changes': [('l2-changes','color')],
  'status':  [('l3-status','color')],
  'opus':    [('l3-opus','color')],  'opuslab': [('l3-opuslab','color')],
  'sep':     [('*separator*','color')],
}

def build(pal):
    bg = pal['bg']
    model, branch, limit = pal['model'], pal['branch'], pal['limit']
    ctx, ses, week = pal['ctx'], pal['ses'], pal['week']
    light = pal.get('light')
    bar_t, timer_t = (.32, .18) if light else (.62, .25)
    roles = {
      'chip1_body': model, 'chip1_icon': mix(model, bg, .45), 'chip1_glyph': pal['glyph'], 'chip1_ink': bg,
      'chip2_body': branch,'chip2_icon': mix(branch, bg, .45),'chip2_glyph': pal['glyph'], 'chip2_ink': bg,
      'chip3_body': limit, 'chip3_icon': mix(limit, bg, .45), 'chip3_glyph': pal['glyph'], 'chip3_ink': bg,
      'm1_bar': mix(ctx, bg, bar_t), 'm1_val': ctx,
      'm2_bar': mix(ses, bg, bar_t), 'm2_val': ses,
      'm3_bar': mix(week, bg, bar_t), 'm3_val': week,
      'timer2': mix(ses, bg, timer_t), 'timer3': mix(week, bg, timer_t),
      'effort': pal['green'], 'speed': pal['blue'], 'cost': pal['green'],
      'changes': pal['yellow'], 'status': pal['green'],
      'opus': mix(model, pal['fg'], .25 if light else .45), 'opuslab': mix(model, bg, .20 if light else .35),
      'sep': pal['sep'],
    }
    cfg = json.load(open(LIVE))
    for role, targets in ROLES.items():
        val = 'hex:' + roles[role]
        for wid, field in targets:
            for line in cfg['lines']:
                for w in line:
                    if wid == '*separator*':
                        if w.get('type') == 'separator': w[field] = val
                    elif w.get('id') == wid:
                        w[field] = val
    return cfg

PALETTES = {
 'panel-palenight': dict(bg='292D3E', fg='A6ACCD', glyph='FFFFFF', model='C792EA', branch='C3E88D',
    limit='FF9CAC', ctx='FFCB6B', ses='F78C6C', week='FF9CAC', green='C3E88D', blue='82AAFF',
    yellow='FFCB6B', sep='5C6685'),
 'panel-dracula': dict(bg='282A36', fg='F8F8F2', glyph='F8F8F2', model='BD93F9', branch='50FA7B',
    limit='FF79C6', ctx='F1FA8C', ses='FFB86C', week='FF79C6', green='50FA7B', blue='8BE9FD',
    yellow='F1FA8C', sep='6272A4'),
 'panel-tokyo-night': dict(bg='1A1B26', fg='A9B1D6', glyph='FFFFFF', model='BB9AF7', branch='9ECE6A',
    limit='F7768E', ctx='E0AF68', ses='FF9E64', week='F7768E', green='9ECE6A', blue='7AA2F7',
    yellow='E0AF68', sep='565F89'),
 'panel-material-light': dict(bg='FAFAFA', fg='546E7A', glyph='FFFFFF', model='7C4DFF', branch='39ADB5',
    limit='E53935', ctx='F6A434', ses='F76D47', week='E53935', green='5B8C1F', blue='3E6AB8',
    yellow='B07000', sep='90A4AE', light=True),
}
for name, pal in PALETTES.items():
    d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
    json.dump(build(pal), open(os.path.join(d, 'settings.json'), 'w'), indent=2, ensure_ascii=False)
    print('built', name)
