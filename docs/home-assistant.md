# Home Assistant

## Package

`homeassistant/packages/ariston_nimbus_ebusd.yaml` contains:

| Entity | What it is |
|---|---|
| `sensor.heat_pump_heat_output` | heat to the water, kW: flow / 60 × 4.186 × (flow − return). **Negative during defrost.** |
| `sensor.heat_pump_cop` | instantaneous COP. Unavailable when heat ≤ 0 or power ≤ 150 W (defrost, standby). |
| `sensor.heat_pump_delta_t` | flow − return, K |
| `sensor.heat_pump_compressor_running_frequency` | compressor Hz, unavailable at 0 Hz (for the hourly minimum) |
| `binary_sensor.heat_pump_defrost` | heat pump status is Defrost |
| `sensor.heat_pump_defrosts_today`, `sensor.heat_pump_defrost_time_today` | history_stats from midnight |
| `sensor.heat_pump_heat_total` | integral of the heat output, kWh (left Riemann sum, 1 min sub-interval) |
| `sensor.heat_pump_heat_today` | daily utility meter of the heat total, `net_consumption: true` because defrost lowers the total |
| `sensor.heat_pump_energy_today` | daily utility meter of the energy counter |
| `sensor.heat_pump_cop_today` | heat today / electricity today, shown from 0.2 kWh on |
| `climate.nimbus_zone_1` | zone 1 control (MQTT): off / heat = Manual / auto = time program, target = comfort temperature |
| automation `nimbus_ebusd_republish_after_start` | publishes `ebusd/list` 30 s after HA starts |

Enable packages in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

### As UI helpers instead

Every item except the climate entity and the automation can also be created in the UI (Settings → Devices &
services → Helpers):
- Template sensor or template binary sensor: use the same templates.
- **Integral**: source `sensor.heat_pump_heat_output`, method Left, max sub-interval 1 min.
- **Utility meter**: daily; for heat turn on *net consumption*, and turn off *periodically resetting* for
  both meters.
- **History stats**: type count / time, start `{{ today_at() }}`, end `{{ now() }}`.

The climate entity can also be published as a retained MQTT discovery message on
`homeassistant/climate/<id>/config` with the same keys plus a `device` block. The broker then keeps it.

## Dashboard

`homeassistant/dashboards/nimbus-ebusd.yaml` has 5 views:

- **Overview**: heat pump tiles, COP gauge, defrost, zone 1 thermostat, energy, 12 h charts.
- **Water temperatures**: 24 h chart of flow (both sensors), return and flow target, plus a delta T chart.
- **Heat pump**: refrigerant circuit, hydraulics, a defrost / heat output chart, and the compressor vs.
  outdoor temperature charts (24 h and hourly over 14 days).
- **Settings**: zone 1 settings read from the bus, and the ebusd connection.

## Energy dashboard

Add the heat pump as an individual device:

- consumption: `sensor.heating_ebusd_energymgr_heat_pump_energy_consumed`;
- power: `sensor.heating_ebusd_heatpump_electrical_power`.

The Energy dashboard has no category for **heat**. Adding the heat total as a device would count it as
electricity, and adding it as gas would show gas. Keep heat on the eBUS dashboard instead.

## Entity IDs

ebusd's discovery (`mqtt-hassio.cfg`) puts all devices in the area *Heating*. With an English HA that gives
IDs like:
- `sensor.heating_ebusd_heatpump_flow_temperature`
- `sensor.heating_ebusd_energymgr_heat_pump_energy_consumed`

If your IDs differ, replace the prefix `heating_ebusd_` in the package and the dashboard.

The 769e "buffer low temperature" entity (`sensor.heating_ebusd_energymgr_buffer_low_temperature`) is the
return echo on systems without a buffer. The dashboard labels it "Return (energy manager)".
