> **DEPRECATED** — This lines-based Clash of Kronos design has been superseded.  
> Canonical spec: [`web-sdk/apps/clash-kronos-cluster/docs/CLASH_KRONOS_CLUSTER_GDD.md`](../../../web-sdk/apps/clash-kronos-cluster/docs/CLASH_KRONOS_CLUSTER_GDD.md)

# Clash of Kronos — Game Design Document (DEPRECATED)

**Studio:** Odd Job Gaming  
**Game:** Clash of Kronos

Use this document as the canonical reference for mechanics, math targets, and SDK alignment for Clash of Kronos (frontend fixtures, math simulations, and book-event design).

---

## Grid

- **5** columns wide, **3** rows tall — **15** total symbol positions.
- Standard **left to right, top to bottom** layout.

---

## Win mechanic

- **Lines-based:** **30 paylines**.
- Wins evaluated **left to right** on active paylines.
- **Minimum 3** matching symbols on a payline triggers a win.
- Winning symbols are **highlighted**, then **removed** from the grid.
- **New symbols drop from above** to fill empty positions — this is the **cascade** mechanic.
- After each cascade, **all 30 paylines** are re-evaluated for new wins.
- Process **repeats until no new wins** are found. Round ends and **cascade tracker resets**.

---

## Cascade tracker — progressive system

A **7-stage** tracker advances by **one stage** each time a cascade produces **at least one winning line**. **Resets to zero** at the start of **every new spin**.

| Stage | Effect |
| ----- | ------ |
| 1 | No effect. Tracker advances. |
| 2 | No effect. Tracker advances. |
| 3 | No effect. Tracker advances. |
| 4 | **Treasure chest dollar symbols activate.** Chests are always present on the reels in every spin but display as **locked and dormant** before stage 4. At stage 4 they **unlock** and become **active**. Any **active** treasure chest that is part of a **winning line** pays its **displayed cash value** on top of the regular line win. |
| 5 | **2×** multiplier applied to **all wins** including active treasure chest cash values. |
| 6 | **3×** multiplier applied to **all wins** including active treasure chest cash values. |
| 7 | **5×** multiplier applied to **all wins** including active treasure chest cash values. |

- **Base game maximum multiplier** is **5×** at stage 7.
- **Free spins mode** uses a **separate tracker table** with different stage values (see [Free spins](#free-spins)).
- **Multipliers do not stack** between base game stages and free spins mode.

---

## Symbol set

| Tier | Count | Role | Names |
| ---- | ----- | ---- | ----- |
| Low | 3 | Appear frequently. Small pay amounts. | `RUNE`, `SHIELD`, `HELMET` |
| Mid | 2 | Appear moderately. Medium pay amounts. | `EAGLE`, `PEGASUS` |
| High | 1 | Appears rarely. Highest regular symbol pay. | `KRONOS_SMALL` |
| Scatter | 1 | **Sun icon.** **3+** anywhere on grid triggers free spins. Not on a payline. | `SCATTER` |
| Dollar / chest | 1 | Treasure chest. Always in reel strips every spin. Locked/greyed before unlock stage; then shows cash value. Pays face value when part of a **winning payline**. | `CHEST` |
| Wild (base) | 1 | Substitutes all **regular** symbols except scatter and chest. Can appear on **all 5 reels**. | `WILD` |

### Wild variants

- **`WILD_LIGHTNING`** — Substitutes like a regular wild. When used in a **winning combination**, on the **next cascade** **2–4** random **regular** symbols are struck by lightning and converted into **wilds**. Lightning effect plays **visually before** the next cascade evaluates.
- **`WILD_SURGE`** — Substitutes like a regular wild. When used in a **winning combination**, on the next cascade a **power surge** hits **all active** treasure chests and **increases their displayed cash values** before the next win evaluation. Triggers even if the next cascade has **no wins** — chest values stay increased for the **remainder of that spin sequence**.
- **`WILD_HAMMER`** — Substitutes like a regular wild. When used in a winning combination the hammer is **collected and held**. Activates when a cascade produces **zero winning lines** (round would otherwise end). Then: **clears all symbols** except **wilds**, **active chests**, and **scatters**; **advances cascade tracker by one stage**; new symbols drop; win evaluation on the new grid. **Hammer consumed after one use.** If new wins occur, round continues; if not, round ends.
- **`WILD_EAGLE`** — **Extremely rare.** Substitutes like a regular wild. On win, activates **all three** power-ups **in sequence**: lightning (2–4 wilds) → surge (chest values) → hammer **collected** for later use. All three resolve **before** the next cascade evaluates.

### Wild power-up rules

- Each wild on the reels is **randomly assigned** one of the four variant types (plus base wild) at **generation time**. Probabilities **weighted**: base wild most common; lightning and surge moderate; hammer less frequent; **golden eagle** very rare.
- **Multiple** power-up wilds can be active in the same spin.
- **Multiple hammer wilds** in one spin: **only one hammer held** — they **do not stack**.
- **Multiple surge** activations in one spin: chest boost can apply **multiple times**.

---

## Free spins

- Triggered by **3+ scatter** symbols **anywhere** on the grid.
- Awards **8** free spins.
- During free spins the cascade tracker uses a **completely separate progression table** from base game. The **10×** at stage 7 in free spins is **not** stacked on base game — it is the **highest stage value exclusive** to free spins.
- **Progressive tracker resets** at the start of **each individual free spin**.
- All wild power-up variants remain **active** during free spins.

### Free spins tracker progression

| Stage | Effect |
| ----- | ------ |
| 1 | No effect. |
| 2 | No effect. |
| 3 | **Treasure chests unlock** (one stage **earlier** than base game). |
| 4 | **2×** multiplier. |
| 5 | **3×** multiplier. |
| 6 | **5×** multiplier. |
| 7 | **10×** multiplier — free spins **maximum**. Replaces and does **not** stack with base game stage 7 (**5×**). |

### Scatter retrigger (during free spins)

Scaled additional spins by scatter count:

| Scatters | Extra spins |
| -------- | ----------- |
| 3 | +5 |
| 4 | +8 |
| 5 | +12 |

- **Bonus buy:** **100×** bet for direct entry into free spins.

---

## Reel strip configuration notes (Math SDK)

- **Chest** symbols: **moderate** frequency on **all 5 reels** — visible on grid in **most** spins without dominating. Suggested **1–3** chest symbols per reel strip.
- **Chest cash values:** range from low to high; **low** values most frequent, **high** rare.
- **Wild variants:** can appear on **all 5 reels**.
- **Scatter:** all **5** reels.
- **Golden eagle wild:** **very low** frequency — **at most 1** occurrence per reel strip.

---

## Math targets

| Target | Note |
| ------ | ---- |
| RTP | ~**96%** |
| Volatility | **Medium–high** |
| Max win | **TBD** through simulation; suggest **5000×–10000×** band. |
| Symbol pays per tier | Tune via simulation. |
| Treasure chest cash value range | Tune via simulation. |
| Wild power-up probability distribution | Tune via simulation. |
| Hit rate | Tune for engagement without over-generosity. |

---

## Key Math SDK implementation notes

- **Cascade tracker** is state that **increments** with each **winning cascade** and **resets** each **new spin** (and per free-spin rules above).
- **Base** and **free spins** each have **their own tracker progression table** — not the same table with a modifier. **Switch** by current game mode.
- **Chest** symbols: **dormant** before stage 4 (base) or stage 3 (free spins) — occupy cell, **no** wins, **no** cash value shown. **Active** after unlock: show **random** cash value; pay when part of a **winning line**.
- **Wild power-ups** must be **book events**: lightning (spawn wilds), surge (modify chest values), hammer (zero-win clear / tracker bump / refill). **All effects must be in the book** for deterministic replay.
- Prefer branching from the **closest cascading lines** example in Math SDK rather than from scratch.

---

## Mirror copy

This file is kept in sync with `web-sdk/apps/clash-of-kronos/docs/CLASH_OF_KRONOS_GDD.md`. Edit one and mirror changes to the other when the design updates.

---

## Document history

- Initial GDD pasted from studio spec for Odd Job Gaming — Clash of Kronos.
