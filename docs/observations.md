# Observations (Nimbus S NET R32 80S-T, November 2026)

Measured on one installation at 1–2 °C outdoor temperature. Single zone, no buffer tank, no DHW.

## How data reaches Home Assistant

Home Assistant never reads the bus itself. ebusd (in the eBUSd app) does three things:
1. It **listens to broadcasts** (`b` lines), for example the energy manager's flow target or the Sensys room
   temperature.
2. It **decodes other masters' reads** (`u` lines). The Sensys reads the heat pump status and the circuit
   pressure every 10 s; ebusd sees the question and the answer.
3. It **polls by itself** (`r` lines). Every `--pollinterval` seconds it sends one read; priority 1 messages
   get a turn every cycle, priority 5 every 5th cycle.

ebusd publishes each decoded value to MQTT (`ebusd/<circuit>/<name>`), and the HA MQTT sensors only
subscribe. The only things HA sends are writes (`.../set`) and `ebusd/list`, which asks ebusd to republish its
cache. `ebusd/list` puts nothing on the bus.

**The energy manager does not poll the heat pump on this bus.** Without the `r1` lines the heat pump values
appear only when the Light Gateway reads them for the cloud, which is rare and never while the cloud is blocked.

## Refresh intervals (measured)

| Data | Interval |
|---|---|
| Polled heat pump groups | ~25 s with 5 polled messages, ~30–36 s with 6 |
| Energy counter (r5) | ~125 s (5 polled messages) |
| Heat pump status, circuit pressure (Sensys reads) | 10 s |
| Energy manager broadcasts (heat request, flow target, return echo) | ~25 s |
| Room temperature (Sensys) | ~2 min, more often on change |
| Settings (`2020`) | on change and every ~30 min |

A poll that loses arbitration is skipped until the next cycle, so some intervals are doubled.

## Flow, flow target and the two flow sensors

- The heat pump outlet temperature `7610` ran about **0.8–1.0 °C above** the energy manager's calculated flow
  target `6197`.
- The energy manager's own flow sensor `6310` reads **0.4–0.5 °C lower than `7610`**, steadily, also after a
  defrost. So about half of the gap is just the two sensors.
- The rest appeared while the compressor sat at its lowest frequency for that temperature (23 Hz): the heat
  pump cannot deliver less heat (~2.7 kW), so the flow stays slightly above target.
- A change of the comfort temperature moves the flow target at once (24 → 23 °C lowered it by ~1.5 °C). The
  compressor needed ~20 min to come down and the water another ~20 min to follow.

## Compressor minimum frequency

- At 1–2 °C outdoor the compressor never went below **23 Hz**.
- In much warmer weather **18 Hz** was seen.
- This suggests the minimum frequency rises in cold weather. That is not confirmed from documentation. The
  "Compressor and outdoor temperature" chart on the dashboard (hourly minimum while running) is there to check it.

## Defrost

Two defrosts were recorded about 2 h 28 min apart, at ~1 °C outdoor.

| | Defrost 1 | Defrost 2 |
|---|---|---|
| Time | 19:09:45–19:12:15 (~2.5 min) | 21:37:24–21:39:14 (1 min 50 s) |
| Compressor | 56 → 33 Hz | 23 Hz → stop (0 W) → 50 Hz / 1235 W → 30 Hz |
| Evaporator | −4 → +5.3 °C | −2 → +27.5 °C |
| Flow / return | 22.0 / 28.3 °C | 21.2 / 27.7 °C |
| Water flow | 22 → 32.7 l/min | 20 → 32.4 l/min |
| Expansion valve | 107 → 500 | 50 → 500 |

The sequence of defrost 2:
1. the compressor stops and the expansion valve opens fully;
2. the circuit runs reversed at 50 Hz, taking heat from the water to melt the ice;
3. it switches back and heats at a slightly higher frequency than before.

The heat taken from the water was about 10–15 kW for roughly a minute, about **0.2 kWh per defrost**. This is
a rough number from only 2–3 samples. Every ~2.5 h, that is about 3 % of the heat.

The energy manager status stays "Heating Cycle" during a defrost. Only the heat pump status `ca46` shows
"Defrost".

## Power and energy

- `7c4f` is the outdoor unit's electrical power in W: compressor, fan and electronics. koszoaron compared it
  with an external meter (r = 0.993); the indoor unit (~100–240 W) is missing from it.
- The counter `52d9+53d9` is in 10 kJ units (/360 = kWh). Check: from 17:56 to 18:49 it went from 179.386 to
  180.425 kWh, consistent with 1.2–1.6 kW.
- Example day start: heat 0.875 kWh / electricity 0.209 kWh, COP 4.19 at ~1 °C outdoor, defrost included.

## Comparison with the Ariston cloud

Identical values at the same time:

| Value | eBUS / cloud |
|---|---|
| Flow | 32.4 / 32.0 °C |
| Outdoor | 2.1 / 2.0 °C |
| Pressure | 1.3 / 1.3 bar |
| Room temperature | 22.9 / 22.9 °C |
| Setpoint | 24 / 24 °C |
| Fixed flow | 28 / 28 °C |
| Curve offset | 0 / 0 |
| Mode | Heating / Heating |
| Heat request | on / on |
| Quiet mode | off / off |

## Writes

- Writes are `2020` broadcasts to `fe`, the same telegrams the Sensys sends.
- The energy manager adopts a write in 6–16 s, and the Sensys display shows the new value. Tested: 24.0 →
  24.5 → 24.0 °C. When the comfort temperature went up, the flow target followed (31.8 → 33.3 °C).
- The mode state can take a few minutes to come back, until the energy manager broadcasts `200e c679`.
