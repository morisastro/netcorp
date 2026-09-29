# NetCorp Tycoon

A desktop management/tycoon game about building your own hosting / cloud infrastructure company — from a garage home lab to a multi-region provider.

> **Status:** Pre-production — specification phase. No playable code yet.

## License

This game is free and licensed under **CC BY-ND 4.0** (Creative Commons Attribution-NoDerivatives 4.0 International).

- You may **copy, distribute and use** the game, even commercially, **with attribution**.
- You may **not** redistribute a **modified** version of the source code or binaries.
- **Mods are allowed** — supplementary packages loaded at runtime via the official modding API are not considered derivative works of the game, provided they are distributed separately and do not embed or replace the game's source code or binaries. Mod authors retain full rights to their own work.

See [LICENSE](LICENSE) for the full text.

## Tech stack

- **Language:** Python 3.11+
- **UI:** PySide6 (Qt for Python)
- **State:** local JSON file (no database, no server)
- **Bundling:** PyInstaller
- **CI:** GitHub Actions (build on tag → release)

## Project structure

```
netcorp-tycoon/
├── main.py                  # entrypoint
├── app/                     # application shell, settings, update checker
├── core/                    # game logic (framework-agnostic, testable)
├── data/                    # static game data (catalogs, balance, generators)
├── persistence/             # save/load
├── ui/                      # PySide6 screens & widgets
└── tests/                   # pytest tests for core logic
```

The `core/` layer is fully separated from `ui/` — game logic knows nothing about Qt and is unit-tested independently. The UI only calls methods on a `Game` object and reads state through `Game.get_state()`.

## Documentation

- [SPEC.md](SPEC.md) — full game specification (gameplay loop, systems, economy, progression, employees, failures, customers, UI screens, data model, roadmap).

## Development

(Setup instructions will be added once the scaffold is in place.)