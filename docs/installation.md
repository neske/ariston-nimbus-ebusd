# Installation

## 1. Adapter

The configuration was made with the **eBUS Adapter Shield C6** stick (https://adapter.ebusd.eu/v5-c6/stick.en).

1. The adapter is always powered over USB-C (5 V, at least 400 mA). It draws nothing from the eBUS and is
   galvanically isolated.
2. First setup: hold the button while plugging in USB, until the LEDs pulse. The adapter opens a WiFi access
   point **`EBUS`**; connect and open `http://192.168.4.1`. Alternatives: WPS, or "Connect to network" at
   https://adapter.ebusd.eu/v5-c6/firmware.en.html over USB in Chrome or Edge.
3. In **Configuration**, enter your WiFi. Host connection: **WiFi**. Protocol: **enhanced**.
4. Give the adapter a fixed IP (a DHCP reservation in the router).
5. **Configuration → eBUS → Advanced Settings: Show → Arbitration Delay, micros = 300.** Without it about
   6–10 % of the polls lost arbitration on this bus.
6. WiFi signal matters. At −77 dBm there were reconnects; at −66 dBm it was stable.

The adapter status page (`/api/v1/status`) and configuration (`/api/v1/config`) can be read over HTTP.

## 2. Wiring (power off!)

- **Switch off the power of the indoor and the outdoor unit.** The same board carries 230 V terminals
  (HV IN, V1/V2, AUX).
- Indoor unit, signal board **M1**, terminals **`EBUS 2` – `B` and `T`**. In the Nimbus Plus S NET R32
  installation manual this is the "BUS connection for system interface" (Fig. 75–76).
- Connect the adapter **in parallel** with the existing bus; the Sensys and Light Gateway stay connected.
- Polarity does not matter for this adapter. Two-wire cable, at least 0.5 mm², total bus length 50 m max.
- Power on. The adapter's green LED **blinks** when it sees bus traffic and stays **steady** without a bus.

## 3. eBUSd app

1. Add the app repository `https://github.com/LukasGrebe/ha-addons` (Settings → Apps → App store → ⋮ →
   Repositories) and install **eBUSd**.
2. Start and stop the app once, so the Supervisor creates `/addon_configs/<slug>_ebusd/`.
3. Copy the **contents** of `ebusd/config/` into that folder, for example with the Samba share app. Result:
   - `/addon_configs/<slug>_ebusd/mqtt-hassio.cfg`
   - `/addon_configs/<slug>_ebusd/ariston/ariston.csv`, `local.csv`, `_templates.csv`

   ebusd also loads subfolders of the config path. Keep only these files under `ariston/`.

### App options

| Option | Value |
|---|---|
| `network_device` | `ens:<adapter IP>` (WiFi, port 9999 by default) or `ens:/dev/ttyACM0` (USB) |
| `seed_mqtt_cfg` | `false` (this repo brings its own `mqtt-hassio.cfg`) |
| Start on boot / Watchdog | on / on |

`commandline_options`, one per line:

```
--scanconfig=off              # never scan the bus
--configpath=/config/ariston/
--mqttjson
--mqttint=/config/mqtt-hassio.cfg
--pollinterval=5              # one polled message every 5 s
--log=all:notice
```

To look at raw telegrams, for example when extending the configuration, add these and remove them again
afterwards (the file ends up in full backups):

```
--lograwdata
--lograwdatafile=/share/ebusd-raw.log
--lograwdatasize=20000        # kB, plus one rotated copy
```

### Read-only first (recommended)

1. Start with `--readonly`, and in `local.csv` turn the `r1`/`r5` lines into `u` lines and remove the two
   `w` lines.
2. Check the log: no `ERR`/`invalid`/`duplicate` while loading, `signal acquired`, MQTT connected.
3. Compare the values with the cloud or the Sensys.
4. Then remove `--readonly` and restore the `r` lines. Polling sends only read telegrams that the Light
   Gateway or the Sensys also send.
5. Add the `w` lines last, after checking them against your own bus.

## 4. Home Assistant

- MQTT integration and a broker (Mosquitto app) are required; ebusd takes the broker credentials from the
  Supervisor.
- Devices **ebusd energymgr / heatpump / sensys / gateway** appear in the area *Heating*, with entity IDs
  like `sensor.heating_ebusd_heatpump_flow_temperature`. Some settings only show up when the Light Gateway or
  a Sensys menu reads them, so they can take up to 30 minutes.
- Package and dashboard: see [home-assistant.md](home-assistant.md).

Useful commands in the app terminal ("Open Web UI"):
- `ebusctl info`
- `ebusctl find -d`
- `ebusctl grab result all` (messages the configuration does not know)
