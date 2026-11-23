# Tools

Small standalone Python 3 scripts for working with an ebusd raw log (`--lograwdata`). They need no packages.

| Script | Usage | Output |
|---|---|---|
| `census.py` | `python census.py RAWLOG [ARISTON_CSV]` | every BridgeNet layout seen (QQ ZZ PBSB register list, count) and which definition in the CSV keys on it |
| `audit.py` | `python audit.py ARISTON_CSV LAYOUTS_TXT` | for each definition, whether the layout it was written for (from its `# … read of …` comment) matches the layouts in your census output |
| `conflicts.py` | `python conflicts.py ariston.csv local.csv` | duplicate names and overlapping keys (same ZZ, PBSB and an ID that is a prefix of the other) |

Save the census output to a file (`python census.py ebusd-raw.log > layouts.txt`) and use it as
`LAYOUTS_TXT` for `audit.py`.

The raw log can contain addresses and values from your own system. Do not publish it without checking.
