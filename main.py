# -*- coding: utf-8 -*-
"""群聊屏蔽：让指定群暂时完全不响应，私聊不受影响。

用途
----
测试或风控观察期，把几个群先静音，只在私聊里跟 Bot 说话。
最高优先级拦截，比 iris / active_reply 都早，不会留下"已读"痕迹。

开关
----
    /mute on      开始屏蔽（默认就开着）
    /mute off     放行
    /mute status  看当前状态

配置里 mute_group_ids 为空时插件不拦截任何消息，等于关闭。
"""

from __future__ import annotations

import time
from typing import Any

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

PLUGIN_NAME = "astrbot_plugin_group_mute"

DEFAULT_CONFIG = {
    "enabled": True,
    "mute_group_ids": [],
    "mute_private": False,
    "log_interval_sec": 600,
}

# 必须早于 tattle(10000) 与 msg_debounce(9999)，否则封禁/合并逻辑先跑
HANDLER_PRIORITY = 50000


class GroupMutePlugin(Star):
    def __init__(self, context: Context, config: Any = None):
        super().__init__(context)
        # self.config 是给读代码方便的合并副本；落盘必须走原始配置对象。
        # 原来 _persist 在 self.config 上找 save_config —— 那是个普通 dict，
        # 永远找不到，于是 /mute off 仍然只在内存生效，重启又开。（审计发现）
        self._raw_config = config if isinstance(config, dict) else None
        self.config = dict(DEFAULT_CONFIG)
        if isinstance(config, dict):
            self.config.update({k: v for k, v in config.items() if k in DEFAULT_CONFIG})
        self._active = bool(self.config.get("enabled", True))
        self._last_log: dict[str, float] = {}

    async def initialize(self) -> None:
        ids = self._ids()
        logger.info(
            f"[group-mute] 就绪，屏蔽 {'开' if self._active else '关'}，"
            f"目标群 {ids or '（未配置，不拦截）'}"
        )

    async def terminate(self) -> None:
        pass

    def _persist(self, on: bool) -> None:
        """把开关写回配置。

        以前 /mute off 只改内存，任何一次 reload / 重启都会回到配置里的值，
        表现就是"我明明关了，它又自己打开了"。开关要能被记住才算开关。
        """
        try:
            self.config["enabled"] = bool(on)
            raw = self._raw_config
            if raw is None:
                logger.warning("[group-mute] 拿不到配置对象，开关只在本进程有效")
                return
            raw["enabled"] = bool(on)
            save = getattr(raw, "save_config", None)
            if callable(save):
                save()
                logger.info(f"[group-mute] 开关已写入配置：enabled={bool(on)}")
            else:
                logger.warning("[group-mute] 配置对象不支持保存，开关只在本进程有效")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"[group-mute] 开关落盘失败: {e}")

    def _ids(self) -> list[str]:
        raw = self.config.get("mute_group_ids") or []
        if isinstance(raw, str):
            raw = [x.strip() for x in raw.replace("，", ",").split(",")]
        return [str(x).strip() for x in raw if str(x).strip()]

    def _should_mute(self, event: AstrMessageEvent) -> str:
        """返回被屏蔽的群号；不屏蔽返回空串。"""
        if not self._active:
            return ""
        ids = self._ids()
        if not ids:
            return ""
        if self.config.get("mute_private"):
            try:
                if event.is_private_chat():
                    return "private"
            except Exception:
                pass
        try:
            gid = str(event.get_group_id() or "").strip()
        except Exception:
            gid = ""
        return gid if gid and gid in ids else ""

    @filter.event_message_type(filter.EventMessageType.ALL, priority=HANDLER_PRIORITY)
    async def mute_gate(self, event: AstrMessageEvent):
        """最高优先级：命中屏蔽名单就掐掉事件，后续所有插件都收不到。"""
        target = self._should_mute(event)
        if not target:
            return

        now = time.time()
        gap = float(self.config.get("log_interval_sec", 600) or 600)
        if now - self._last_log.get(target, 0) >= gap:
            self._last_log[target] = now
            logger.info(f"[group-mute] 已屏蔽 {target} 的消息（不回复）")

        event.stop_event()
        return

    @filter.command("mute")
    async def mute_cmd(self, event: AstrMessageEvent):
        """屏蔽开关：/mute on | off | status"""
        try:
            is_admin = event.is_admin() is True
        except Exception:
            is_admin = False
        if not is_admin:
            yield event.plain_result("仅管理员可用。")
            return

        arg = (event.message_str or "").replace("/mute", "", 1).strip().lower()
        if arg == "on":
            self._active = True
            self._persist(True)
            yield event.plain_result(f"屏蔽已开启：{self._ids() or '（名单为空）'}")
        elif arg == "off":
            self._active = False
            self._persist(False)
            yield event.plain_result("屏蔽已关闭，群聊恢复响应。")
        elif arg == "status":
            yield event.plain_result(
                f"屏蔽 {'开' if self._active else '关'} | 名单 {self._ids() or '空'}"
                f" | 私聊{'也屏蔽' if self.config.get('mute_private') else '不受影响'}"
            )
        else:
            yield event.plain_result("用法：/mute on | off | status")
