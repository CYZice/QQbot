"""消息过滤器 - 判断是否需要响应消息"""
import re
from typing import Dict, Any
from loguru import logger
from config.bot_config import WAKE_WORDS, MONITORED_GROUPS


class MessageFilter:
    """消息过滤器 - 判断消息是否需要 bot 响应"""

    def __init__(self, bot_qq: int):
        """
        初始化消息过滤器

        Args:
            bot_qq: Bot 的 QQ 号
        """
        self.bot_qq = bot_qq
        self.wake_word_patterns = [re.compile(word) for word in WAKE_WORDS]

    def should_respond(self, message_data: Dict[str, Any]) -> bool:
        """
        判断是否应该响应该消息

        Args:
            message_data: NapCat 发来的消息数据

        Returns:
            True 如果需要响应，False 如果不需要
        """
        # 检查消息类型
        if message_data.get("post_type") != "message":
            return False

        if message_data.get("message_type") != "group":
            return False

        # 检查是否在监听的群中
        group_id = message_data.get("group_id")
        if group_id not in MONITORED_GROUPS:
            logger.debug(f"群 {group_id} 不在监听列表中")
            return False

        # 检查是否是 bot 自己发的消息
        if message_data.get("user_id") == self.bot_qq:
            return False

        message_text = message_data.get("message", "")

        # 检查是否 @ 了 bot
        if self.is_at_bot(message_text):
            logger.info(f"检测到 @ bot: {message_text[:50]}")
            return True

        # 检查是否包含唤醒词
        if self.has_wake_word(message_text):
            logger.info(f"检测到唤醒词: {message_text[:50]}")
            return True

        return False

    def is_at_bot(self, message_text: str) -> bool:
        """
        检查消息是否 @ 了 bot

        Args:
            message_text: 消息文本（包含 CQ 码）

        Returns:
            True 如果 @ 了 bot
        """
        # CQ 码格式: [CQ:at,qq=123456]
        at_pattern = rf"\[CQ:at,qq={self.bot_qq}\]"
        return bool(re.search(at_pattern, message_text))

    def has_wake_word(self, message_text: str) -> bool:
        """
        检查消息是否包含唤醒词

        Args:
            message_text: 消息文本

        Returns:
            True 如果包含唤醒词
        """
        for pattern in self.wake_word_patterns:
            if pattern.search(message_text):
                return True
        return False

    def clean_message(self, message_text: str) -> str:
        """
        清理消息文本，移除 CQ 码等

        Args:
            message_text: 原始消息文本

        Returns:
            清理后的消息文本
        """
        # 移除 @ 相关的 CQ 码
        cleaned = re.sub(r"\[CQ:at,qq=\d+\]", "", message_text)

        # 移除其他常见 CQ 码（保留文本内容）
        # 例如: [CQ:face,id=123] -> 移除
        cleaned = re.sub(r"\[CQ:[^\]]+\]", "", cleaned)

        # 去除多余空格
        cleaned = cleaned.strip()

        return cleaned
