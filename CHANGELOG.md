# 更新日志

所有重要变更记录于此。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-10-20

### 新增

- 首个公开版本。
- 最高优先级拦截（50000），早于所有消息处理插件
- `/mute on` / `/mute off` / `/mute status` 随时开关
- 状态持久化到配置文件，重启 / 热重载后保持
- 同一群最多每 `log_interval_sec` 秒写一条日志，不刷屏

