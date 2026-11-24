# Web research

## Input shaper (2026-11-25)

- No published SV04 resonance frequencies found.
- Klipper docs: [Resonance Compensation](https://www.klipper3d.org/Resonance_Compensation.html),
  example frequencies and the `[input_shaper]` format.
- Dual carriage + input shaper: [Klipper Discourse #7603](https://klipper.discourse.group/t/native-dual-carriage-support-in-input-shaping/7603)
  (set SET_INPUT_SHAPER per carriage, keep `[input_shaper]` empty), fix for dual carriage SK init in
  PR #6938 ([Discourse](https://klipper.discourse.group/t/issue-with-hybrid-corexy/23324?page=2)).
- Sovol forum: [SV08 stock values](https://forum.sovol3d.com/t/input-shaper-settings-sovol-ships-with-speed-benchy-settings/9945),
  [narrow resonance_tester range](https://forum.sovol3d.com/t/poor-x-axis-input-shaper/8853), not SV04.

## Mainsail without KIAUH (2026-11-25)

- The MainsailOS image via the Raspberry Pi Imager is the recommended route
  ([MainsailOS](https://github.com/mainsail-crew/mainsailos), [Voron docs](https://docs.vorondesign.com/build/software/installing_mainsail.html),
  [All3DP](https://all3dp.com/2/mainsailos-simply-explained/)).
- MainsailOS doesn't include KlipperScreen. Guides use KIAUH for it, but it also works with the official installer.
- No current information on Docker/prind for the Pi found.

## KlipperScreen without KIAUH (2026-11-25)

- `git clone https://github.com/KlipperScreen/KlipperScreen.git` → `./KlipperScreen/scripts/KlipperScreen-install.sh`
  ([iFixit guide](https://www.ifixit.com/Guide/Installing+Klipper+Screen/152182)).
- update_manager entry: `origin https://github.com/KlipperScreen/KlipperScreen.git`,
  `virtualenv ~/.KlipperScreen-env`, `requirements scripts/KlipperScreen-requirements.txt`,
  `managed_services KlipperScreen`.

## llmwiki.app (2026-11-25)

- [llmwiki.app](https://llmwiki.app/): open-source (Apache 2.0) implementation of Karpathy's LLM Wiki,
  hosted (Polybius LLC) or self-hosted. Layers: raw sources / wiki / schema, operations Ingest/Query/Lint.
  Content goes to Anthropic for generation ([privacy](https://llmwiki.app/privacy)).
  Decision: adopt the pattern inside the repo, don't use the service.
