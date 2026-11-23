# Ariston Nimbus Plus S NET R32 – local eBUS integration for Home Assistant

Local monitoring and basic control of an **Ariston Nimbus Plus S NET R32** heat pump in Home Assistant.
It uses [ebusd](https://github.com/john30/ebusd) and an eBUS adapter, and talks over the Ariston BridgeNet
bus. No cloud is needed. The Ariston cloud integration and the Light Gateway can stay as they are; they work
side by side.

This is a working configuration from one installation:
- single zone heating, no domestic hot water, no cooling, **no buffer tank**;
- Sensys HD room controller and Light Gateway on the bus.

It builds on [koszoaron/ebusd-ariston-nimbus](https://github.com/koszoaron/ebusd-ariston-nimbus) (Nimbus Plus
110 M T NET). That work is adapted to the frame layouts this system sends, plus the reads the heat pump needs
here. See [NOTICE.md](NOTICE.md).

> **Use at your own risk.** BridgeNet is fragile: a full bus scan crashed another user's boiler. Read
> [Safety rules](#safety-rules) before you connect anything.

## What you get

| Data | Source on the bus | Refresh |
|---|---|---|
| Flow, return, water flow, evaporator, condenser, suction, discharge, compressor Hz, expansion valve, **electrical power** | ebusd polls the heat pump (r1) | ~30 s |
| Heat pump status (Heating, **Defrost**, …) | Sensys read, decoded passively | 10 s |
| Heating circuit pressure | Sensys read, decoded passively | 10 s |
| Energy manager: flow target (heating curve), zone mode, heat request, setpoints | broadcasts | ~25 s / on change |
| Energy manager's own flow sensor (6310) | ebusd polls (r1) | ~30 s |
| **Energy counter** (kWh, outdoor unit) | ebusd polls (r5) | ~2–3 min |
| Room temperature (Sensys) | broadcast | ~2 min |
| Zone 1 **mode** (off / manual / time program) and **comfort temperature** | **write**, same broadcast as the Sensys | on demand |

On top of that, the Home Assistant package adds:
- heat output (kW, negative during defrost) and delta T;
- instantaneous and **daily COP**;
- defrost detection with count and duration per day;
- a `climate` entity for zone 1;
- a 5-view dashboard.

Details: [docs/observations.md](docs/observations.md).

## Hardware

- **eBUS Adapter Shield C6** (stick version, by john30), over WiFi or USB. Any ebusd-compatible adapter with
  the *enhanced* protocol should work.
- Wiring: indoor unit, signal board **M1**, terminals **`EBUS 2` – `B` and `T`**, in parallel with the
  existing bus. Polarity does not matter for this adapter. **Switch off the power of both units before
  opening.** See [docs/installation.md](docs/installation.md).

## Quick start

1. Install the **eBUSd** app: add the repository `https://github.com/LukasGrebe/ha-addons` in the app store.
2. Copy `ebusd/config/` into the app's config folder, `/addon_configs/<slug>_ebusd/`. You should end up with
   `mqtt-hassio.cfg` and `ariston/*.csv` there.
3. Set the app options as shown in [docs/installation.md](docs/installation.md#app-options), in particular
   `--scanconfig=off`, `--configpath=/config/ariston/` and `--pollinterval=5`. Start the app.
4. In the adapter's web UI set **Arbitration delay = 300 µs**.
5. Copy `homeassistant/packages/ariston_nimbus_ebusd.yaml` to `/config/packages/` and restart Home Assistant.
6. Create a dashboard and paste `homeassistant/dashboards/nimbus-ebusd.yaml` in the raw configuration editor.
7. Optional: add `sensor.heating_ebusd_energymgr_heat_pump_energy_consumed` to the Energy dashboard as an
   individual device ([docs/home-assistant.md](docs/home-assistant.md#energy-dashboard)).

## Repository layout

```
ebusd/config/                  -> /addon_configs/<slug>_ebusd/
├── mqtt-hassio.cfg            HA discovery (filter-seen=1, filter-direction=r|^u$, definition-retain=1)
└── ariston/
    ├── ariston.csv            koszoaron's passive definitions, 10 of them disabled (#local-disabled)
    ├── local.csv              this system's definitions: passive, polled (r1/r5) and 2 writes
    └── _templates.csv         value lists (from koszoaron)
homeassistant/
├── packages/ariston_nimbus_ebusd.yaml   templates, daily COP, defrost, climate, automation
└── dashboards/nimbus-ebusd.yaml         dashboard
docs/                          installation, registers, observations, HA notes, troubleshooting
tools/                         small raw-log analysis scripts
```

## Safety rules

- **Never** scan the bus (`--scanconfig=off`). Never poll or send `203a`/`203b`.
- Keep `filter-seen = 1` in `mqtt-hassio.cfg`.
- Polled reads are the same telegrams the Light Gateway or Sensys already send. Do not add reads of
  registers you have not seen on your own bus.
- Every write goes to the energy manager's EEPROM. Do not write from automations that change values often.
- Before enabling writes, capture your own bus while you change mode and temperature on the Sensys, and check
  that the telegrams match the `w` lines in `local.csv` (`2020 c679` and `2020 6271`). Another firmware can
  use other registers.

## Status and limits

- Tested on one installation, 2026-11. Home Assistant 2026.11, ebusd 26.1, eBUSd app 26.1.10.
- Not implemented: cancelling a temporary Sensys override, DHW, cooling, other zones, plant mode.
- A few rare settings broadcasts still do not match a definition: winter mode delay/threshold, outdoor
  temperature correction and buffer charge mode.
- COP uses the outdoor unit's power (register `7c4f`). The indoor unit (circulator, electronics) is not
  included, so the COP reads slightly high.

## License

GPL-3.0, like the configuration it is based on. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
