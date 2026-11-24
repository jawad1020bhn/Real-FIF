# Real-FIF — FIFA 14 DB (FC 27 Roster Update)

This repository contains a FIFA 14 `fifa_ng_db` database updated with FC 27 roster/data while preserving the original FIFA 14 DB schema.

## Current state

- **Branch work merged from:** `arena/e35b71b3-real-fif`
- **Source template:** [ViniMacacari/eafc-db-kit — FC 27](https://github.com/ViniMacacari/eafc-db-kit/tree/main/templates/FC%2027)
- **DB format:** EA FIFA NG DB (`DB\x00\x08`), FIFA 14 schema (`fifa_ng_db-meta.xml`)
- **Release:** [fc27-roster-update](https://github.com/jawad1020bhn/Real-FIF/releases/tag/fc27-roster-update)

## Files

| File | Description |
|---|---|
| `fifa_ng_db.db` | Updated FIFA 14 database |
| `fifa_ng_db-meta.xml` | Original FIFA 14 schema/metadata (unchanged) |

## What was updated

Data was imported from the FC 27 main `fifa_ng_db.db` into the existing FIFA 14 schema-compatible tables/columns.

| Table | Result |
|---|---:|
| `playernames` | +15,837 added, 27,229 updated (43,066 total) |
| `players` | 14,614 updated, 7,009 added from FC 27; 2,277 FC 27 women players removed after review (25,305 total) |
| `teams` | 638 updated, 232 added; 107 women/special FC 27 teams removed (922 total) |
| `teamplayerlinks` | Rebuilt from FC 27 roster, then cleaned for removed women players/teams (20,899 total) |
| `leagues` | 40 updated, 17 added; 7 women leagues removed (55 total) |
| `nations` | 217 updated, 2 added (231 total) |
| `playerloans` | Rebuilt from FC 27 (645 total) |
| `teamstadiumlinks` | Updated from FC 27, then cleaned for removed women teams (922 total) |

## Women content removal

- Removed **2,277 women players** from FC 27 (`gender == 1`) that were not present in the original FIFA 14 DB.
- Removed **107 associated teams** that had women players in FC 27 (women-only clubs plus the FC 27 special mixed "Look Book Character Team"), their stadium links, and dangling team links.
- Removed **7 women leagues** (`iswomencompetition == 1` in FC 27).
- FIFA 14 `players` schema has no `gender` field; removal was performed by matching FC 27 player IDs.

## Important limitations

- **Schema-compatible only.** FC 27-only fields (playstyles, roles, new FC attributes, etc.) are not part of the FIFA 14 schema and were not imported. FIFA 14-only fields were preserved for matched existing records.
- **FIFA 14-only fields for newly added FC 27 players:** `attackingworkrate=1`, `defensiveworkrate=1` (medium), `marking` estimated from `(standingtackle + slidingtackle + interceptions) / 3`, `faceposercode/animpenaltieskickstylecode/animpenaltiesmotionstylecode = 0`. Matched existing players kept their original FIFA 14-only values.
- **Range clamping:** 64,492 integer values were clamped to valid FIFA 14 field ranges during import. Most were defaults for newly added teams hitting `rangeLow`; some were real overflows (e.g. FC 27 stadium IDs above FIFA 14 9-bit max 511 were clamped to 511).
- **Not updated:** kits/teamkits, formations/tactics, competitions/fixtures, graphics/faces/audio assets, career structure tables, and other FIFA 14-specific content/assets. This is a core roster/data update, not a full mod pack.
- **Validation:** DB was written/read back through `eafc-db-kit` `FifaDatabaseService` against the FIFA 14 XML descriptor. Spot checks: Messi (158023) OVR 89, Ronaldo (20801) OVR 84, Mbappé (231747) OVR 91.

## Release

GitHub release: [FC 27 Roster Update (FIFA 14 DB, no women players/clubs)](https://github.com/jawad1020bhn/Real-FIF/releases/tag/fc27-roster-update)

> Note: asset upload via `gh release upload` failed in the sandbox with GitHub uploads EOF; files are available in the repo/branch. Manual upload:
> ```bash
> gh release upload fc27-roster-update fifa_ng_db.db fifa_ng_db-meta.xml --clobber
> ```
