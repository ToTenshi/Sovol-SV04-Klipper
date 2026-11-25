#!/usr/bin/env python3
"""Simulate the SV04 Z offset handling without a printer.

Renders the real macros with Klipper's Jinja delimiters and command parser (so names that
Klipper can't call show up as UNKNOWN COMMAND) and models Z_OFFSET_APPLY_PROBE,
SAVE_CONFIG/restart and tool changes. Every scenario must end at the target z_offset 1.800.

Usage: python3 tools/simulate_z_offset.py [config folder]   (needs: pip install jinja2)
"""
import ast
import collections
import configparser
import glob
import os
import re
import shlex
import sys

import jinja2

cfgdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'SV04-with-display')
ARGS_R = re.compile(r'([A-Z_]+|[A-Z*])')
macros, renamed = {}, {}
for f in sorted(glob.glob(os.path.join(cfgdir, '*.cfg'))):
    if f.endswith('variables.cfg'): continue
    cp = configparser.RawConfigParser(strict=False, inline_comment_prefixes=(';', '#')); cp.read(f)
    for sec in cp.sections():
        if sec.startswith('gcode_macro '):
            o = dict(cp.items(sec)); n = sec.split(None, 1)[1].strip().upper()
            macros[n] = {'tpl': o['gcode'], 'vars': {k[9:]: ast.literal_eval(v) for k, v in o.items() if k.startswith('variable_')}}
            if 'rename_existing' in o: renamed[o['rename_existing'].upper()] = n
env = jinja2.Environment('{%', '%}', '{', '}')
Coord = collections.namedtuple('Coord', 'x y z e')
class A(dict):
    def __getattr__(s, k):
        try: return s[k]
        except KeyError: raise AttributeError(k)
st = dict(gofs=[0.0, 0.0, 0.0], c0='PRIMARY', c1='INACTIVE', ext='extruder', state='standby',
          loaded=1.50, pending={}, sv={'dual_x_offset': 0.0, 'dual_y_offset': 0.0, 'dual_z_offset': 0.10})
saved, log = {}, []
def printer():
    p = A(dual_carriage=A(carriage_0=st['c0'], carriage_1=st['c1']),
          toolhead=A(extruder=st['ext'], position=Coord(150, 150, 10, 0), axis_maximum=Coord(302, 302, 400, 0), homed_axes='xyz'),
          gcode_move=A(homing_origin=Coord(*st['gofs'], 0)), save_variables=A(variables=A(st['sv'])),
          configfile=A(save_config_pending=bool(st['pending']), save_config_pending_items=A({k: A(v) for k, v in st['pending'].items()}),
                       settings=A(bltouch=A(z_offset=st['loaded'])),
                       config=A(stepper_x=A(position_endstop='-65'), dual_carriage=A(position_endstop='360'),
                                bed_mesh=A(mesh_min='10,45', mesh_max='290, 270', probe_count='6,6'))),
          print_stats=A(state=st['state']), idle_timeout=A(state='Printing' if st['state'] == 'printing' else 'Ready'),
          manual_probe=A(is_active=False))
    for h in ('extruder', 'extruder1', 'heater_bed'): p[h] = A(target=0.0, temperature=25.0, can_extrude=True)
    p['fan_generic fanX1'] = A(speed=0.0); p['fan_generic fanX2'] = A(speed=0.0)
    for n, m in macros.items(): p['gcode_macro ' + n] = A(m['vars'])
    return p
def run(script, depth=0):
    for line in script.split('\n'):
        line = line.split(';')[0].strip()
        if not line or line.startswith('#'): continue
        parts = ARGS_R.split(line.upper()); cmd = parts[1] + parts[2].strip() if len(parts) >= 3 else ''
        rest = line.split(None, 1)[1] if ' ' in line else ''
        params = {}
        for tok in shlex.split(rest):
            if '=' in tok: k, v = tok.split('=', 1); params[k.upper()] = v
        if cmd in macros and cmd not in renamed.values() or cmd in macros:
            m = macros[cmd]; ctx = dict(m['vars']); ctx.update(printer=printer(), params=params, rawparams=rest)
            run(env.from_string(m['tpl']).render(ctx), depth + 1); continue
        if cmd == 'SET_GCODE_VARIABLE':
            macros[params['MACRO'].upper()]['vars'][params['VARIABLE'].lower()] = ast.literal_eval(params['VALUE'])
        elif cmd == 'SAVE_VARIABLE': st['sv'][params['VARIABLE']] = ast.literal_eval(params['VALUE'])
        elif cmd == 'SET_GCODE_OFFSET':
            for i, a in enumerate('XYZ'):
                if a in params: st['gofs'][i] = float(params[a])
                elif a + '_ADJUST' in params: st['gofs'][i] += float(params[a + '_ADJUST'])
        elif cmd == 'SET_DUAL_CARRIAGE':
            c = int(params['CARRIAGE']); mode = params.get('MODE', 'PRIMARY').upper()
            if mode == 'PRIMARY': st['c0'], st['c1'] = ('PRIMARY', 'INACTIVE') if c == 0 else ('INACTIVE', 'PRIMARY')
            else: st['c1'] = mode
        elif cmd == 'ACTIVATE_EXTRUDER': st['ext'] = params['EXTRUDER']
        elif cmd == 'SAVE_GCODE_STATE': saved[params.get('NAME', 'default')] = list(st['gofs'])
        elif cmd == 'RESTORE_GCODE_STATE': st['gofs'] = list(saved[params.get('NAME', 'default')])
        elif cmd == 'Z_OFFSET_APPLY_PROBE_BASE':      # Klipper: new = loaded z_offset - homing_origin.z
            st['pending'].setdefault('bltouch', {})['z_offset'] = '%.3f' % (st['loaded'] - st['gofs'][2])
        elif cmd == 'PROBE_CALIBRATE_RESULT':
            st['pending'].setdefault('bltouch', {})['z_offset'] = params['Z']
        elif cmd == 'RESPOND' and 'error' in rest.lower(): log.append('ERROR ' + rest[:90])
        elif cmd == 'RESPOND' and 'SAVE_Z_OFFSET|' in rest: log.append('PROMPT offers SAVE_Z_OFFSET')
        elif cmd not in KNOWN: log.append('UNKNOWN COMMAND ' + cmd)
KNOWN = {'G28', 'G1', 'G0', 'G90', 'G91', 'G92', 'M400', 'M117', 'M220', 'M221', 'M83', 'M104', 'M109', 'M140', 'M190', 'RESPOND', 'CLEAR_PAUSE',
         'SET_HEATER_TEMPERATURE', 'TEMPERATURE_WAIT', 'Z_TILT_ADJUST', 'BED_MESH_CALIBRATE_BASE', 'BED_MESH_CLEAR', 'SET_FAN_SPEED',
         'SET_INPUT_SHAPER', 'SYNC_EXTRUDER_MOTION', 'DGUS_PRINT_START', 'DGUS_PRINT_END', 'TURN_OFF_HEATERS', 'M84', 'M106', 'G4',
         'UPDATE_DELAYED_GCODE', 'PROBE_CALIBRATE', 'MANUAL_PROBE', 'SAVE_CONFIG'}
def restart():   # SAVE_CONFIG: pending -> loaded, Klipper restart clears gcode offsets and macro variables
    if 'bltouch' in st['pending']: st['loaded'] = float(st['pending']['bltouch']['z_offset'])
    st['pending'] = {}; st['gofs'] = [0.0, 0.0, 0.0]; macros['_SOVOL_TOOL_OFFSET']['vars']['applied_z'] = 0.0
    st['c0'], st['c1'], st['ext'] = 'PRIMARY', 'INACTIVE', 'extruder'
def effective(tool):   # nozzle height reference while printing: loaded z_offset minus babystep of that tool
    tool_z = st['sv']['dual_z_offset'] if tool == 1 else 0.0
    return st['loaded'] - (st['gofs'][2] - tool_z)
START = 'START_PRINT EXTRUDER=0 EXTRUDERS=1 EXTRUDER_TEMP=210 EXTRUDER1_TEMP=0 BED_TEMP=60 AREA_START=100,100 AREA_END=150,150'
DUAL1 = 'START_PRINT EXTRUDER=1 EXTRUDERS=2 EXTRUDER_TEMP=210 EXTRUDER1_TEMP=210 BED_TEMP=60 AREA_START=100,100 AREA_END=150,150'
def show(t, tool=0): print(f'{t:70s} effective z_offset T{tool} = {effective(tool):.3f}' + (f'   [{"; ".join(log)}]' if log else '')); log.clear()

print('Target value is 1.800 (loaded 1.500)\n--- A: Z_OFFSET_CALIBRATE measured 1.800, NOT saved, print started')
run('PROBE_CALIBRATE_RESULT Z=1.800'); st['state'] = 'printing'; run(START); show('print right after calibration (no restart)')
run('END_PRINT'); st['state'] = 'complete'; restart(); run(START); show('after SAVE_CONFIG / restart, next print'); run('END_PRINT')

for label, save in (('B: Mainsail panel (babystep buttons + save button)', 'Z_OFFSET_APPLY_PROBE'), ('C: our macro SAVE_Z_OFFSET', 'SAVE_Z_OFFSET')):
    restart(); st['loaded'] = 1.50; print(f'--- {label}')
    st['state'] = 'printing'; run(START); run('SET_GCODE_OFFSET Z_ADJUST=-0.30 MOVE=1'); show('babystep -0.30 during print')
    run(save); show(f'after {save} (no restart)')
    run('END_PRINT'); st['state'] = 'complete'; run(START); show('next print WITHOUT restart'); run('END_PRINT')
    restart(); run(START); show('next print AFTER SAVE_CONFIG / restart'); run('END_PRINT')

restart(); st['loaded'] = 1.50; print('--- D: babystep while T1 prints (dual), saved with the Mainsail button')
st['state'] = 'printing'; run(DUAL1); show('dual print started with T1', 1)
run('SET_GCODE_OFFSET Z_ADJUST=-0.30 MOVE=1'); run('Z_OFFSET_APPLY_PROBE'); show('babystep -0.30 on T1, Mainsail save', 1)
run('T0'); show('tool change to T0', 0); run('END_PRINT'); st['state'] = 'complete'
restart(); run(START); show('after restart, T0 print', 0); run('END_PRINT')

restart(); st['loaded'] = 1.50; print('--- E: babystep never saved')
st['state'] = 'printing'; run(START); run('SET_GCODE_OFFSET Z_ADJUST=-0.30 MOVE=1'); st['state'] = 'complete'
log.clear(); run('END_PRINT'); print('    END_PRINT:', log or ['NO SAVE PROMPT']); log.clear()
run(START); show('next print without restart (babystep kept, like Klipper)')
print('--- F: CALIBRATE_Z_T1 while a T0 value is still pending')
st['pending'] = {'bltouch': {'z_offset': '1.700'}}; st['state'] = 'standby'; run('CALIBRATE_Z_T1'); print('   ', log); log.clear()
