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

## Installer menu 4.2 (zone 1 heating curve)

Captured passively on 2026-11-25 while the menu was opened and changed on the Sensys. Opening a menu item
sends `70 fe 2001 <reg>`; the energy manager answers `13 fe 200e <reg> <value> <min> <max>`. A change is
`70 fe 2020 <reg> <value>`, and the energy manager confirms it with `13 fe 2010`. These registers are not in
`local.csv`.

| Menu | Register | Format | Value seen | Range reported |
|---|---|---|---|---|
| 4.2.0 Zone temperature range | `0081` | UCH, 0 low temp / 1 high temp | 0 | 0–1 |
| 4.2.1 Thermoregulation | `c079` | UCH, 0 fixed flow, 1 basic, 2 room only, 3 outdoor only, 4 room + outdoor | 4 | 0–4 |
| 4.2.2 Slope | `6a71` | UIN /100 | 0.40 | 0.20–1.00 |
| 4.2.3 Offset | `6471` | SIN /10 °C | +1.0 | −7.0…+7.0 |
| 4.2.4 Room influence | `c279` | UCH | 2 | 0–80 (the manual says 0–20) |
| 4.2.5 Max flow temperature | `6071` | UIN /10 °C | 40.0 | 20.0–45.0 |
| 4.2.6 Min flow temperature | `6171` | UIN /10 °C | 20.0 | 20.0–40.0 |
| 4.2.7 Thermoregulation logic | `db89` | UCH, 0 classic / 1 smart | 0 | 0–1 |
| 4.2.8 Quick night setback | `0881` | UCH | 0 | 0–1 |
| 4.2.9 Heat request mode | `ce79` | UCH, 0 standard, 1 RT time program exclusion, 2 forced | 0 | 0–2 |

At about 3.5 °C outdoor, lowering the slope from 0.40 to 0.30 and raising the offset from +1 to +2 moved the
flow target `6197` from 31.6 to 30.3 °C. During the changes the energy manager also broadcast `2010 42f7`
(`18 19` → `18 1b` → `18 1c`); its meaning is unknown.

## Installer menu 1.6 (water circulation)

Captured the same way on 2026-11-25. Here the Sensys reads the energy manager directly: `70 18 2001 <reg>`,
reply `<value> <min> <max>`, all UCH. All values are the factory defaults.

| Menu | Register | Value seen | Range reported |
|---|---|---|---|
| 1.6.0 CH pump prerun time | `d527` | 30 s | 30–255 |
| 1.6.1 Time for prerun new attempt | `d627` | 90 s | 0–100 |
| 1.6.2 CH pump overrun | `d727` | 3 min | 0–16 |
| 1.6.3 Pump speed control | `c32a` | 2 = modulating (0 low, 1 high) | 0–2 |
| 1.6.4 Antifreeze HP circulator speed | `c58f` | 1 = medium (0 low, 2 high) | 0–2 |

## Installer menu 13.4 (heat pump water circulation)

The Sensys reads these from the heat pump: `70 1e 2001 <reg>`, reply `<value> <min> <max>`.

| Menu | Register | Format | Value seen | Range reported |
|---|---|---|---|---|
| 13.4.4 Target delta T for pump modulation | `7b2b` | UIN /10 K | 5.0 | 5.0–20.0 |
| 13.4.5 Max PWM pump | `d32c` | UCH % | 100 | 55–100 |
| 13.4.6 Min PWM pump | `d22c` | UCH % | 55 | 40–100 |

With 55 % minimum PWM this system's pump does not go below ~20 l/min, so at 3–5 kW the delta T stays near 3 K
although the target is 5 K.

## Installer menus 13.10 and 13.9 (heat pump diagnostics)

The Sensys reads these from the heat pump (`70 1e 2001`). 2-byte registers report min `8000` and max `7fff`
(no limits). Values from 2026-11-25 18:20, compressor at 21 Hz, ~3.5 °C outdoor.

| Menu | Register | Format | Value seen |
|---|---|---|---|
| 13.10.0 Inverter capacity (probably) | `6947` | SIN | 8 (8 kW model; read after the others) |
| 13.10.1 Actual compressor frequency | `cb46` | UCH Hz | 21 |
| 13.10.2 Set compressor modulation (probably) | `c446` | UCH | 100 |
| 13.10.3 Electric heater 1 | `1c45` | UCH 0/1 | 0 |
| 13.10.5 Fan 1 rpm | `6e4f` | SIN rpm | 655–660 |
| 13.10.6 Fan 2 rpm | `6f4f` | SIN rpm | 0 |
| 13.10.7 Expansion valve | `704f` | SIN steps | 50 |
| 13.10.8 Expansion valve 2 | `554f` | UIN | 0 |
| 13.9.0 Heat pump mode | `ca46` | UCH | 3 |
| 13.9.1 Last inverter error | `c54b` | UCH | 0 |
| 13.9.2 Safety thermostat | `0316` | UCH 0/1 | 1 |
| 13.9.3 Flowmeter | `6e13` | SIN /10 l/min | 15.7 |
| 13.9.4 Flow switch | `0c45` | UCH 0/1 | 1 |
| 13.9.5 Inverter shut-off protection | `1045` | UCH 0/1 | 0 |
| 13.9.6 Evaporator pressure | `6c4f` | SIN /10 bar | 7.3 |
| 13.9.7 Condenser pressure | `6d4f` | SIN /10 bar | 19.3–19.5 |

The pressures fit R32 saturation at about −3 °C and 32 °C. Expansion valve 2 is `554f`, so `714f` is not the
second expansion valve.

## Installer menus 4.1 and 1.5 (winter mode, energy manager parameters)

Menu 4.1 is read with `70 fe 2001` (reply `13 fe 200e`), menu 1.5 with `70 18 2001`.

| Menu | Register | Format | Value seen | Range reported |
|---|---|---|---|---|
| 4.1.0 Automatic winter mode | `0781` | UCH 0/1 | 0 (off) | 0–1 |
| 4.1.1 Automatic winter mode threshold | `7971` | SIN /10 °C | 20.0 | 0.0–30.0 |
| 4.1.2 Automatic winter mode delay | `7a71` | UIN min | 300 | 0–600 |
| 1.5.0 Min pressure | `c42a` | UCH /10 bar | 0.4 | 0.3–0.4 |
| 1.5.1 Warning pressure | `c52a` | UCH /10 bar | 0.6 | 0.4–0.8 |
| 1.5.2 Outdoor T for boiler disabling | `7126` | SIN /10 °C | 35.0 | −25.0–40.0 |
| 1.5.3 Outdoor T for HP disabling | `7226` | SIN /10 °C | −25.0 | −25.0–35.0 |
| 1.5.4 HP disabling outdoor T, DHW | `638f` | SIN /10 °C | −25.0 | −25.0–35.0 |
| 1.5.5 External temperature correction | `7426` | SIN /10 °C | 0.0 | −3.0–+3.0 |
| 1.5.9 Filling pressure | `c02a` | UCH /10 bar | 1.2 | 0.9–1.5 |

This explains the unmatched settings broadcasts: on this bus the energy manager groups them as
`13 fe 2020 7971 c800 7a71 2c01 0782 00` and `13 fe 2020 0520 01 602b c003 7426 0000`, not in the layouts
of the upstream definitions.

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
