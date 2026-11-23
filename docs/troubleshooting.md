# Troubleshooting

## `arbitration lost` in the ebusd log

Several masters share the bus. Set the adapter's **Arbitration Delay to 300 µs**: Configuration → eBUS →
Advanced Settings: Show. Before that, 6–10 % of the polls were lost; after it, very few. A lost poll is just
retried in the next cycle.

## Reconnects or `signal lost`

Usually WiFi. Check the RSSI on the adapter's status page: at −77 dBm there were problems, at −66 dBm it was
stable. Give the adapter a fixed IP and use `network_device: ens:<IP>`. Without an adapter, mDNS fails and the
watchdog restarts the app in a loop.

## Entities stay `unknown` after an HA restart

ebusd publishes a value only when it changes or is read again. `definition-retain = 1` in `mqtt-hassio.cfg`
keeps the entities, and the package's automation publishes `ebusd/list` after start, so ebusd republishes its
cache. You can also publish `ebusd/list` (empty payload) by hand from the MQTT integration.

## `invalid position` while decoding

The frame is shorter than the definition. Ariston devices send the same register in different combinations,
so a definition must cover only the common prefix of the layouts that appear on *your* bus.
- Capture raw data (`--lograwdata`) and run `tools/census.py <rawlog> <csv>` to see which layouts appear and
  which definition matches them.
- `tools/audit.py` compares a CSV's documented layouts with yours.

## Stale entities after disabling a definition

With retained discovery, removed definitions leave entities behind. Delete them in HA, or publish an empty
retained payload to their `homeassistant/.../config` topic.

## Undo the writes

1. Remove the two `w` lines from `local.csv` and restart the app.
2. Remove the `mqtt: climate:` block from the package, or publish an empty retained payload to the climate's
   discovery topic if you created it that way.

## Ariston cloud integration blocked (HTTP 429)

This is not caused by ebusd. Ariston NET v0.20.7 (library ariston 0.19.16) also fetches menu items for heat
pump systems, which adds several requests per refresh. After a 429 it retries after 5 s, which keeps the
account blocked ("Requests are blocked"). Upstream issue: fustom/ariston-remotethermo-home-assistant-v3#545.

What helped here:
- going back to v0.20.6 (library 0.19.15; it fetches the extra menus only for hybrid systems);
- a scan interval of 600 s;
- disabling the integration for a while so the block can expire.

All the data that matters is local over eBUS anyway.
