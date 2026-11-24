# Bus devices and registers

## Devices on the bus

| Address (master / slave) | Device |
|---|---|
| 13 / 18 | Energy manager (indoor unit) |
| 03 / 1e | Heat pump (outdoor unit) |
| 70 / 75 | Sensys HD |
| 7f / 84 | Light Gateway (cloud) |
| 31 / 36 | ebusd (adapter) |
| 00 | a master that sends `203a` broadcasts now and then (not ebusd) |

## Commands (PBSB) used by Ariston BridgeNet

| PBSB | Meaning |
|---|---|
| `2000` | multi read: request = list of 2-byte register IDs, reply = mask byte + values |
| `2001` | single read: reply = value, min, max (sent by Sensys menus, ~1/s while a menu is open) |
| `200e`, `200f`, `2010` | broadcasts of values (`fe`) |
| `2020` | settings broadcast; also the **write** command (a broadcast to `fe` that the energy manager adopts) |

Value width follows the first byte of the register ID:
- `00`–`1f` and `c0`–`df`: 1 byte;
- `40`–`7f`: 2 bytes, little endian, signed. Temperatures are ×10.

## Definitions in `local.csv`

### Polled by ebusd (`r1`, `r5`)

| Message | Target | Registers → fields |
|---|---|---|
| `grp_7610_7710_6e13` | heat pump 1e, `2000` | 7610 flow temperature, 7710 return temperature, 6e13 water flow (/10 l/min) |
| `grp_7910_7117_7217` | heat pump 1e, `2000` | 7910 evaporator, 7117 condenser outlet, 7217 suction temperature |
| `grp_7317_ca46_cb46` | heat pump 1e, `2000` | 7317 discharge temperature, ca46 heat pump status, cb46 compressor frequency (Hz) |
| `grp_704f_7c4f` | heat pump 1e, `2000` | 704f expansion valve position, 7c4f **electrical power (W)** of the outdoor unit |
| `ch_flow_temp` | energy manager 18, `2001` | 6310 energy manager's own flow sensor |
| `hp_energy_consumed` (`r5`) | energy manager 18, `2000` | 52d9+53d9: 32-bit counter in 10 kJ units, /360 = kWh. It adds up `7c4f`, so it has the same errors |
| `hp_heat_produced` (`r5`) | energy manager 18, `2000` | 46d9+47d9: heat produced, same format. The energy manager and the Light Gateway read it every 2 h |

All of them are the same telegrams the Light Gateway (2000) or the Sensys menu (2001) send to these devices.

### Passive

| Message | Sender | Registers |
|---|---|---|
| `grp_d140_ca46` (u) | Sensys → heat pump, every 10 s | ca46 heat pump status |
| `grp_4dfd_7547_c700`, `grp_7547_c700` (u) | Sensys → energy manager, every 10 s | 7547 heating circuit pressure (/10 bar, confirmed against the cloud) |
| `buffer_low_temp` (b) | energy manager | 769e; with no buffer tank it echoes the heat pump return |
| `z1_heat_request_onoff` (b) | energy manager | 0191 zone 1 heat request |
| `z1_mode_state` (b) | energy manager | c194 mode state, 6996 room setpoint |
| `grp_6047_6197` (b) | energy manager | 6047 flow setpoint, 6197 zone 1 calculated flow target |
| `grp_6071_6171_6471` (b, `2020`, every 30 min) | energy manager | 6071 max flow, 6171 min flow, 6471 heating curve offset |
| `z1_room_temp_200f`, `z1_room_temp_2010` (b) | Sensys | 7118 room temperature |
| `menu_*` (u, `2001`) | Sensys menu | 7610, 7710, 6e13, 0c45 flow switch, 7910, 7217, 7317, 7117, 7810 outdoor air (HP sensor), cb46, 7547, c200 circulator |

### Writes (`w`)

| Message | Telegram | Values |
|---|---|---|
| `z1_mode_set` | `fe 2020 c679 <UCH>` | 0 = off, 2 = manual, 3 = time program |
| `z1_comfort_temp_set` | `fe 2020 6271 <UIN ×10>` | 10.0–30.0 °C in 0.5 steps |

Recorded from the Sensys on this bus, for example:
- `70 fe 2020 03 c679 02` sets Manual;
- `70 fe 2020 04 6271 dc00` sets 22.0 °C.

## Heat pump status `ca46`

Values seen on this system: **Heating** and **Defrost (9)**. During a defrost the energy manager status
(`energymgr_status`) stays "Heating Cycle", so `ca46` is the only defrost indicator.

## Disabled upstream definitions (`#local-disabled` in `ariston.csv`)

| Definition | Reason |
|---|---|
| `buffer_high_temp`, `buffer_high_temp_alt`, `buffer_high_temp_alt2` | there is no buffer tank (759e = 0x7fff); one layout misread 649f as 40.0 °C |
| `buffer_low_temp` | different layout; replaced in `local.csv` |
| `z1_heat_request_onoff`, `z1_mode_state` | different layout; replaced in `local.csv` |
| `z1_lwt_max`, `z1_lwt_min` | different 2020 layout; replaced by `grp_6071_6171_6471` |
| `expansion_valve`, `hp_energy_consumed` | the `u` lines would collide with the polled `r` lines in `local.csv` |

Use `tools/conflicts.py ariston.csv local.csv` after an edit to find duplicate names or overlapping keys.
