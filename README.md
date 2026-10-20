# 群聊屏蔽：指定群完全不响应，私聊不受影响

> AstrBot 插件 · 最高优先级拦截，早于记忆与主动回复

## 它解决什么问题

测试期或风控观察期，需要把几个群先静音，只在私聊里跟模型说话。

这条拦截必须比记忆、主动回复、防抖都早，否则会留下「已读」痕迹或产生多余的模型调用。

## 功能

- 最高优先级拦截（50000），早于所有消息处理插件
- `/mute on` / `/mute off` / `/mute status` 随时开关
- 状态持久化到配置文件，重启 / 热重载后保持
- 同一群最多每 `log_interval_sec` 秒写一条日志，不刷屏

## 工作机制

每条消息 → mute_gate(priority=50000)
    ├─ 会话在 mute_group_ids 里 → stop_event()，后续插件收不到
    └─ 否则放行

私聊默认不受影响（mute_private=false）。
mute_group_ids 为空时插件不拦截任何消息，等于关闭。

## 安装

### 方式一：插件市场（推荐）

WebUI 插件市场搜索「群聊屏蔽」。

### 方式二：Releases 下载

从 [Releases](../../releases) 下载 zip，WebUI → 插件 → 上传安装。

### 方式三：手动克隆

```bash
cd AstrBot/data/plugins
git clone https://github.com/RandyLuaW/astrbot_plugin_group_mute.git
```

无额外 Python 依赖。

## 配置项

| 键 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `enabled` | bool | `true` | 启用群聊屏蔽。关闭后不拦截任何消息。 |
| `mute_group_ids` | list | `[]` | 要屏蔽的群号列表。留空则不拦截任何消息（默认留空，需自己填）。 |
| `mute_private` | bool | `false` | 是否连私聊一起屏蔽。默认 false，只在群里静音。 |
| `log_interval_sec` | int | `600` | 同一个群最多多久写一条屏蔽日志（秒），避免刷日志。 |

## 注意事项

- `/mute off` 会写回配置文件，重启后仍然是放行状态
- 屏蔽是彻底不响应，不是延迟响应

## License

MIT
