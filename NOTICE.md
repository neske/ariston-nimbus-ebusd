# Notice

This project is a modified version of **koszoaron/ebusd-ariston-nimbus**
(https://github.com/koszoaron/ebusd-ariston-nimbus, commit `52e54c7`, GPL-3.0).

Files taken from it:

| File | Changes |
|---|---|
| `ebusd/config/ariston/ariston.csv` | 10 definitions commented out with `#local-disabled`, because the frame layouts on this bus differ or the sensor does not exist (buffer). Otherwise unchanged. |
| `ebusd/config/ariston/_templates.csv` | unchanged |
| `ebusd/config/mqtt-hassio.cfg` | `definition-retain = 1`, so the MQTT broker keeps the discovery configs across Home Assistant restarts. Otherwise unchanged. The file comes from the ebusd project (john30/ebusd) and was adapted upstream. |

New in this project:
- `ebusd/config/ariston/local.csv`;
- everything under `homeassistant/`, `docs/` and `tools/`.

Other configurations reviewed for comparison (nothing copied):
- wrongisthenewright/ebusd-configuration-ariston-bridgenet;
- claytonn73/ariston-nimbus-ebusd;
- tweetgeek/ebusd-configuration-ariston-nimbus.

Do not mix them in one ebusd config path: two definitions with the same name or ID make ebusd reject the whole
configuration.

ebusd is by john30 (https://github.com/john30/ebusd), the eBUSd Home Assistant app by LukasGrebe
(https://github.com/LukasGrebe/ha-addons).

Ariston, Nimbus, Sensys and BridgeNet are trademarks of Ariston Group. This project is not affiliated with or
endorsed by Ariston.
