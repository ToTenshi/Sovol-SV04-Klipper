#!/usr/bin/env python3
"""Simulate the SV04 Z offset handling without a printer.

Renders the real macros with Klipper's Jinja delimiters and command parser (names Klipper
can't call show up as UNKNOWN COMMAND) and models Klipper's gcode_move exactly like
klippy/extras/gcode_move.py: G1 without Z keeps the physical height, SET_GCODE_OFFSET
without MOVE only takes effect on the next Z move, RESTORE_GCODE_STATE MOVE=1 returns to the
saved toolhead position, Z_OFFSET_APPLY_PROBE stores "loaded z_offset - G-code offset".

A "true" printer is modelled: real probe z_offset P_TRUE and real height difference of the
T1 nozzle D_TRUE. Every check prints the ERROR of the real nozzle height above the bed
compared with the height the slicer asked for. It must be 0.000.

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

P_TRUE = 1.80   # real distance nozzle T0 <-> bed when the probe triggers
D_TRUE = 0.12   # T1 nozzle tip is 0.12 mm lower than T0 -> T1 needs a +0.12 offset

cfgdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'SV04-with-display')
ARGS_R = re.compile(r'([A-Z_]+|[A-Z*])')
env = jinja2.Environment('{%', '%}', '{', '}')
Coord = collections.namedtuple('Coord', 'x y z e')


class A(dict):
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)


def load_macros():
    macros = {}
    for f in sorted(glob.glob(os.path.join(cfgdir, '*.cfg'))):
        if f.endswith('variables.cfg'):
            continue
        cp = configparser.RawConfigParser(strict=False, inline_comment_prefixes=(';', '#'))
        cp.read(f)
        for sec in cp.sections():
            if sec.startswith('gcode_macro '):
                o = dict(cp.items(sec))
                macros[sec.split(None, 1)[1].strip().upper()] = {
                    'tpl': o['gcode'], 'vars': {k[9:]: ast.literal_eval(v) for k, v in o.items() if k.startswith('variable_')}}
    return macros


KNOWN = {'G28', 'M400', 'M117', 'M118', 'M220', 'M221', 'M82', 'M83', 'M104', 'M109', 'M140', 'M190', 'M106', 'M107', 'M84',
         'RESPOND', 'CLEAR_PAUSE', 'SET_HEATER_TEMPERATURE', 'TEMPERATURE_WAIT', 'Z_TILT_ADJUST', 'BED_MESH_CALIBRATE_BASE',
         'BED_MESH_CLEAR', 'SET_FAN_SPEED', 'SET_INPUT_SHAPER', 'SYNC_EXTRUDER_MOTION', 'DGUS_PRINT_START', 'DGUS_PRINT_END',
         'TURN_OFF_HEATERS', 'G4', 'UPDATE_DELAYED_GCODE', 'PROBE_CALIBRATE', 'MANUAL_PROBE', 'SAVE_CONFIG', 'G92', 'G21'}


class Printer:
    def __init__(self, loaded=1.50, dual_z=0.0):
        self.macros = load_macros()
        self.last = [150.0, 150.0, 10.0, 0.0]   # toolhead (kinematic) position
        self.base = [0.0, 0.0, 0.0, 0.0]
        self.homing = [0.0, 0.0, 0.0, 0.0]
        self.absolute = True
        self.saved = {}
        self.c0, self.c1, self.ext = 'PRIMARY', 'INACTIVE', 'extruder'
        self.state = 'standby'
        self.loaded = loaded
        self.pending = {}
        self.sv = {'dual_x_offset': 0.0, 'dual_y_offset': 0.0, 'dual_z_offset': dual_z}
        self.log = []

    # --- status objects -------------------------------------------------------------
    def status(self):
        p = A(dual_carriage=A(carriage_0=self.c0, carriage_1=self.c1),
              toolhead=A(extruder=self.ext, position=Coord(*self.last), axis_maximum=Coord(302, 302, 400, 0), homed_axes='xyz'),
              gcode_move=A(homing_origin=Coord(*self.homing), gcode_position=Coord(*[l - b for l, b in zip(self.last, self.base)])),
              save_variables=A(variables=A(self.sv)),
              configfile=A(save_config_pending=bool(self.pending), save_config_pending_items=A({k: A(v) for k, v in self.pending.items()}),
                           settings=A(bltouch=A(z_offset=self.loaded)),
                           config=A(stepper_x=A(position_endstop='-62'), dual_carriage=A(position_endstop='360'),
                                    bed_mesh=A(mesh_min='10,30', mesh_max='290,290', probe_count='6,6'))),
              print_stats=A(state=self.state), idle_timeout=A(state='Printing' if self.state == 'printing' else 'Ready'),
              manual_probe=A(is_active=False), probe=A(last_z_result=0.0))
        for h in ('extruder', 'extruder1', 'heater_bed'):
            p[h] = A(target=0.0, temperature=25.0, can_extrude=True)
        p['fan_generic fanX1'] = A(speed=0.0)
        p['fan_generic fanX2'] = A(speed=0.0)
        for n, m in self.macros.items():
            p['gcode_macro ' + n] = A(m['vars'])
        return p

    # --- Klipper gcode_move semantics ----------------------------------------------
    def g1(self, params):
        for i, axis in enumerate('XYZ'):
            if axis in params:
                v = float(params[axis])
                self.last[i] = self.last[i] + v if not self.absolute else v + self.base[i]

    def set_offset(self, params):
        delta = [0.0] * 4
        for i, axis in enumerate('XYZ'):
            if axis in params:
                off = float(params[axis])
            elif axis + '_ADJUST' in params:
                off = float(params[axis + '_ADJUST']) + self.homing[i]
            else:
                continue
            delta[i] = off - self.homing[i]
            self.base[i] += delta[i]
            self.homing[i] = off
        if int(params.get('MOVE', 0)):
            for i in range(3):
                self.last[i] += delta[i]

    def run(self, script):
        for line in script.split('\n'):
            line = line.split(';')[0].strip()
            if not line or line.startswith('#'):
                continue
            parts = ARGS_R.split(line.upper())
            cmd = parts[1] + parts[2].strip() if len(parts) >= 3 else ''
            rest = line.split(None, 1)[1] if ' ' in line else ''
            params = {}
            for tok in shlex.split(rest):
                if '=' in tok:
                    k, v = tok.split('=', 1)
                    params[k.upper()] = v
                elif re.match(r'^[A-Za-z][-0-9.]', tok):
                    params[tok[0].upper()] = tok[1:]
            if cmd in self.macros:
                m = self.macros[cmd]
                ctx = dict(m['vars'])
                ctx.update(printer=self.status(), params=params, rawparams=rest)
                self.run(env.from_string(m['tpl']).render(ctx))
            elif cmd in ('G1', 'G0'):
                self.g1(params)
            elif cmd == 'G90':
                self.absolute = True
            elif cmd == 'G91':
                self.absolute = False
            elif cmd == 'G28':
                self.last[:3] = [150.0, 150.0, 10.0]
            elif cmd == 'SET_GCODE_OFFSET':
                self.set_offset(params)
            elif cmd == 'SAVE_GCODE_STATE':
                self.saved[params.get('NAME', 'default')] = (list(self.last), list(self.base), list(self.homing), self.absolute)
            elif cmd == 'RESTORE_GCODE_STATE':
                last, base, homing, absolute = self.saved[params.get('NAME', 'default')]
                self.absolute, self.base[:3], self.homing = absolute, list(base[:3]), list(homing)
                if int(params.get('MOVE', 0)):
                    self.last[:3] = list(last[:3])
            elif cmd == 'SET_GCODE_VARIABLE':
                self.macros[params['MACRO'].upper()]['vars'][params['VARIABLE'].lower()] = ast.literal_eval(params['VALUE'])
            elif cmd == 'SAVE_VARIABLE':
                self.sv[params['VARIABLE']] = ast.literal_eval(params['VALUE'])
            elif cmd == 'SET_DUAL_CARRIAGE':
                c, mode = int(params['CARRIAGE']), params.get('MODE', 'PRIMARY').upper()
                if mode == 'PRIMARY':
                    self.c0, self.c1 = ('PRIMARY', 'INACTIVE') if c == 0 else ('INACTIVE', 'PRIMARY')
                else:
                    self.c1 = mode
            elif cmd == 'ACTIVATE_EXTRUDER':
                self.ext = params['EXTRUDER']
            elif cmd == 'Z_OFFSET_APPLY_PROBE_BASE':     # klippy/extras/probe.py
                self.pending.setdefault('bltouch', {})['z_offset'] = '%.3f' % (self.loaded - self.homing[2])
            elif cmd == 'RESPOND':
                if 'error' in rest.lower():
                    self.log.append('ERROR ' + rest[:100])
                elif 'SAVE_Z_OFFSET|' in rest:
                    self.log.append('PROMPT offers SAVE_Z_OFFSET')
            elif cmd not in KNOWN:
                self.log.append('UNKNOWN COMMAND ' + cmd)

    def restart(self):   # SAVE_CONFIG + restart: pending -> loaded, offsets and macro variables reset
        if 'bltouch' in self.pending:
            self.loaded = float(self.pending['bltouch']['z_offset'])
        self.pending, self.homing, self.base = {}, [0.0] * 4, [0.0] * 4
        self.c0, self.c1, self.ext = 'PRIMARY', 'INACTIVE', 'extruder'
        self.macros = load_macros()

    def height_error(self, wanted):
        """real nozzle height above the bed minus the height the slicer wants"""
        t1 = self.c1 == 'PRIMARY'
        real = self.last[2] + (P_TRUE - self.loaded) - (D_TRUE if t1 else 0.0)
        return real - wanted


START = 'START_PRINT EXTRUDER={t} EXTRUDERS={n} EXTRUDER_TEMP=210 EXTRUDER1_TEMP=210 BED_TEMP=60 AREA_START=100,100 AREA_END=150,150'
results = []


def check(p, label, wanted=0.2):
    """slicer: layer at Z=wanted, then extrusion moves in X/Y only"""
    err = p.height_error(wanted)
    ok = abs(err) < 0.0005
    results.append(ok)
    extra = f'   [{"; ".join(p.log)}]' if p.log else ''
    p.log.clear()
    tool = 'T1' if p.c1 == 'PRIMARY' else 'T0'
    print(f'  {"OK " if ok else "BAD"} {label:62s} {tool} error {err:+.3f} mm{extra}')


def layer(p, z=0.2):
    p.run(f'G1 Z{z} F600\nG1 X120 Y120 F6000')


print(f'True printer: probe z_offset {P_TRUE:.2f}, T1 {D_TRUE:.2f} mm longer. Every error must be +0.000.\n')

print('A: Z_OFFSET_CALIBRATE measured 1.80 (loaded 1.50), NOT saved, print started')
p = Printer(loaded=1.50)
p.pending = {'bltouch': {'z_offset': '1.800'}}
p.state = 'printing'; p.run(START.format(t=0, n=1)); layer(p); check(p, 'first layer before SAVE_CONFIG')
p.run('END_PRINT'); p.restart(); p.run(START.format(t=0, n=1)); layer(p); check(p, 'after SAVE_CONFIG/restart')

for label, save in (('B: Mainsail panel (babystep + save button)', 'Z_OFFSET_APPLY_PROBE'), ('C: SAVE_Z_OFFSET', 'SAVE_Z_OFFSET')):
    print(label)
    p = Printer(loaded=1.50)
    p.state = 'printing'; p.run(START.format(t=0, n=1)); layer(p)
    p.run('SET_GCODE_OFFSET Z_ADJUST=-0.30 MOVE=1'); p.run('G1 X121 Y121'); check(p, 'babystep -0.30 during print')
    p.run(save); p.run('END_PRINT'); p.run(START.format(t=0, n=1)); layer(p); check(p, f'next print after {save}, no restart')
    p.run('END_PRINT'); p.restart(); p.run(START.format(t=0, n=1)); layer(p); check(p, 'after SAVE_CONFIG/restart')

print('D: dual print after CALIBRATE_Z_T1 (T1 offset 0.12 saved), slicer sends NO Z after the tool change')
p = Printer(loaded=P_TRUE, dual_z=D_TRUE)
p.state = 'printing'; p.run(START.format(t=0, n=2)); layer(p); check(p, 'T0 first layer')
p.run('T1'); p.run('G1 X130 Y130'); check(p, 'T1 after tool change (X/Y moves only)')
p.run('T0'); p.run('G1 X131 Y131'); check(p, 'T0 after tool change back')
p.run('G1 Z0.4 F600\nG1 X100 Y100'); p.run('T1'); p.run('G1 X132 Y132'); check(p, 'T1 on layer 2', 0.4)
p.run('END_PRINT'); p.state = 'complete'; p.run(START.format(t=0, n=1)); layer(p); check(p, 'next print T0')

print('E: T1 saved too small (0.05 instead of 0.12) -> corrected by babystep while T1 prints, saved via Mainsail')
p = Printer(loaded=P_TRUE, dual_z=0.05)
p.state = 'printing'; p.run(START.format(t=0, n=2)); layer(p)
p.run('T1'); p.run('G1 X130 Y130'); err = p.height_error(0.2); print(f'      T1 is {err:+.3f} mm off -> babystep')
p.run(f'SET_GCODE_OFFSET Z_ADJUST={-err:.3f} MOVE=1'); p.run('G1 X131 Y131'); check(p, 'T1 after babystep')
p.run('Z_OFFSET_APPLY_PROBE'); check(p, 'T1 after the Mainsail save button')
p.run('T0'); p.run('G1 X132 Y132'); check(p, 'T0 after tool change (must NOT inherit the T1 babystep)')
print(f'      saved: dual_z_offset={p.sv["dual_z_offset"]:.3f}, probe pending={p.pending.get("bltouch", {}).get("z_offset", "-")}')
p.run('END_PRINT'); p.restart(); p.run(START.format(t=0, n=2)); layer(p); check(p, 'next print T0 after restart')
p.run('T1'); p.run('G1 X133 Y133'); check(p, 'next print T1 after restart')

print('F: probe 0.30 off AND T1 offset too small: babystep T0 (applies to both), then T1, END_PRINT saves')
p = Printer(loaded=1.50, dual_z=0.05)
p.state = 'printing'; p.run(START.format(t=0, n=2)); layer(p)
p.run('SET_GCODE_OFFSET Z_ADJUST=-0.30 MOVE=1'); p.run('G1 X121 Y121'); check(p, 'T0 corrected by babystep')
p.run('T1'); p.run('G1 X130 Y130'); err = p.height_error(0.2)
print(f'      T1 inherits the T0 correction, remaining T1 error {err:+.3f} mm -> babystep on T1')
p.run(f'SET_GCODE_OFFSET Z_ADJUST={-err:.3f} MOVE=1'); p.run('G1 X131 Y131'); check(p, 'T1 corrected by babystep')
p.run('T0'); p.run('G1 X132 Y132'); check(p, 'T0 after tool change (keeps only its own correction)')
p.state = 'complete'; p.log.clear(); p.run('END_PRINT')
print('      END_PRINT:', p.log or ['NO SAVE PROMPT']); p.log.clear()
p.run('SAVE_Z_OFFSET'); p.restart(); p.run(START.format(t=0, n=2)); layer(p); check(p, 'T0 after save + restart')
p.run('T1'); p.run('G1 X130 Y130'); check(p, 'T1 after save + restart')

print('G: Z_OFFSET_DOWN 6 x 0.05 during the print, SAVE_Z_OFFSET, limit')
p = Printer(loaded=1.50)
p.state = 'printing'; p.run(START.format(t=0, n=1)); layer(p)
for _ in range(6):
    p.run('Z_OFFSET_DOWN STEP=0.05')
p.run('G1 X125 Y125'); check(p, 'after 6 x Z_OFFSET_DOWN')
p.run('SAVE_Z_OFFSET'); p.run('END_PRINT'); p.restart(); p.run(START.format(t=0, n=1)); layer(p); check(p, 'after SAVE_CONFIG/restart')
before = p.homing[2]; p.run('Z_OFFSET_UP STEP=1.5'); blocked = p.homing[2] == before
results.append(blocked); print(f'  {"OK " if blocked else "BAD"} limit: Z_OFFSET_UP STEP=1.5 blocked'); p.log.clear()

print('H: CALIBRATE_Z_T1 while a T0 value is still pending')
p = Printer(); p.pending = {'bltouch': {'z_offset': '1.700'}}; p.run('CALIBRATE_Z_T1')
refused = any('first' in l for l in p.log); results.append(refused)
print(f'  {"OK " if refused else "BAD"} refused: {p.log[:1]}')

print(f'\n{sum(results)}/{len(results)} checks OK')
sys.exit(0 if all(results) else 1)
