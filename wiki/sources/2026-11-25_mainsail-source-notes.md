# Findings from the Mainsail source

Read via `gh api repos/mainsail-crew/mainsail/contents/<file>` (branch develop), 2026-11-25.

- `src/store/gui/macros/types.ts`: `GuiMacrosState { mode: 'simple'|'expert', hiddenMacros: string[], macrogroups: {[key]: GuiMacrosStateMacrogroup} }`,
  group `{ id, name, color, colorCustom?, showInStandby, showInPrinting, showInPause, macros?: [{ pos, name, color, showInStandby, showInPrinting, showInPause }] }`.
- `src/store/gui/macros/actions.ts` groupUpload: `server.database.post_item { namespace: 'mainsail', key: 'macros.macrogroups.' + id, value }`.
  New ids via `uuidv4()`.
- `src/store/gui/macros/getters.ts` getAllMacrogroups: `{...group, id}` (id from the key), `caseInsensitiveSort(…, 'name')`.
- `src/store/gui/getters.ts` getAllPossiblePanels: in `expert` mode `'macrogroup_' + group.id`, the `macros` panel is removed.
  getPanels: missing panels are appended visibly in column 1.
- `src/store/printer/getters.ts` getMacros: hides names starting with `_` and macros with `rename_existing` in the settings.
- `src/components/panels/MacrogroupPanel.vue`: matching `existMacro.name.toLowerCase() === macro.name.toLowerCase()`.
  Macros that don't exist are filtered out. Visibility: standby = `standby|cancelled|complete|error`, `paused`, `printing`.
- `src/store/gui/actions.ts` initDb: when the namespace is missing, it only writes the defaults from
  `<config>/.theme/default.json` (if present) and `initVersion`. `saveSetting` writes individual keys
  (`macros.mode` etc.) only when they change. So the key `macros` is missing in a fresh install.
