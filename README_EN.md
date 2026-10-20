# Group Mute: silence selected groups entirely

> AstrBot plugin · Highest-priority gate, before memory and proactive reply

## The problem

During testing or risk-control observation, some groups need to be silenced while private chat keeps working.

The interception must run before memory, proactive reply and debounce plugins, otherwise it leaves read-marks or wastes model calls.

## Features

- Highest-priority gate (50000)
- `/mute on` / `/mute off` / `/mute status`
- State persisted to the config file, survives restarts
- Per-group log throttling

## Install

### Option 1: Plugin marketplace (recommended)

Search "群聊屏蔽" in the AstrBot WebUI plugin marketplace.

### Option 2: Download from Releases

Grab the zip from [Releases](../../releases), then WebUI → Plugins → Upload.

### Option 3: Clone manually

```bash
cd AstrBot/data/plugins
git clone https://github.com/RandyLuaW/astrbot_plugin_group_mute.git
```

No extra Python dependencies.

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `enabled` | bool | `true` | See Chinese README |
| `mute_group_ids` | list | `[]` | See Chinese README |
| `mute_private` | bool | `false` | See Chinese README |
| `log_interval_sec` | int | `600` | See Chinese README |

## Notes

- `/mute off` writes back to the config file
- Muting means no response at all, not a delayed one

## License

MIT
