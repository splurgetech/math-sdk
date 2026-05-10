# Clash of Kronos — math-sdk (fresh Stake Engine)

This checkout is the **canonical StakeEngine/math-sdk** clone used to simulate and publish math for **Clash of Kronos**.

- **Cloned:** 2026-05-10 from `https://github.com/StakeEngine/math-sdk.git` at `origin/main` (see `git log -1`).
- **Game folder:** `games/0_0_clash_of_kronos/` — copied from `games/0_0_lines`; `game_config.py` uses `game_id = "0_0_clash_of_kronos"` and `working_name = "Clash of Kronos"`.
- **Cursor / VS Code:** open **`../web-sdk/clash-of-kronos.code-workspace`** so both SDKs show under one project named **clash-of-kronos** (sibling `web-sdk` + `math-sdk` folders).

## Setup & run

```bash
make setup
# activate the venv per Makefile output, then:
make run GAME=0_0_clash_of_kronos
```

Python **3.12+** recommended (see upstream README).
