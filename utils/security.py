"""安全检查模块 - 消息长度和频率限制"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from loguru import logger
from config.bot_config import MAX_MESSAGE_LENGTH, MAX_MESSAGES_PER_MINUTE


class SecurityLimiter:
    """安全限制器 - 防止消息过长和发送频率过高"""

    def __init__(self):
        # 记录每个群的消息发送时间戳
        # key: group_id, value: list of timestamps
        self.message_timestamps: Dict[int, list] = defaultdict(list)

        # 记录违规次数
        self.violation_count: Dict[int, int] = defaultdict(int)

        # 暂停服务的群
        self.paused_groups: set = set()

    def check_message_length(self, message: str, max_length: int = MAX_MESSAGE_LENGTH) -> bool:
        """
        检查消息长度是否超限

        Args:
            message: 要检查的消息
            max_length: 最大长度限制

        Returns:
            True 如果消息长度合法，False 如果超限
        """
        if len(message) > max_length:
            logger.warning(f"消息长度超限: {len(message)} > {max_length}")
            return False
        return True

    def check_rate_limit(self, group_id: int, max_per_minute: int = MAX_MESSAGES_PER_MINUTE) -> bool:
        """
        检查发送频率是否超限

        Args:
            group_id: 群号
            max_per_minute: 每分钟最大消息数

        Returns:
            True 如果频率合法，False 如果超限
        """
        current_time = time.time()

        # 清理 1 分钟前的时间戳
        self.message_timestamps[group_id] = [
            ts for ts in self.message_timestamps[group_id]
            if current_time - ts < 60
        ]

        # 检查是否超限
        if len(self.message_timestamps[group_id]) >= max_per_minute:
            logger.warning(f"群 {group_id} 发送频率超限: {len(self.message_timestamps[group_id])} 条/分钟")
            return False

        # 记录本次发送时间
        self.message_timestamps[group_id].append(current_time)
        return True

    def handle_violation(self, group_id: int, violation_type: str):
        """
        处理违规行为

        Args:
            group_id: 群号
            violation_type: 违规类型（'length' 或 'rate'）
        """
        self.violation_count[group_id] += 1

        logger.error(
            f"群 {group_id} 发生 {violation_type} 违规，"
            f"累计违规次数: {self.violation_count[group_id]}"
        )

        # 如果违规次数过多，暂停该群的服务
        if self.violation_count[group_id] >= 3:
            self.paused_groups.add(group_id)
            logger.critical(f"群 {group_id} 因多次违规已暂停服务！")

    def is_group_paused(self, group_id: int) -> bool:
        """检查群是否被暂停服务"""
        return group_id in self.paused_groups

    def resume_group(self, group_id: int):
        """恢复群的服务"""
        if group_id in self.paused_groups:
            self.paused_groups.remove(group_id)
            self.violation_count[group_id] = 0
            logger.info(f"群 {group_id} 服务已恢复")

    def check_all(self, group_id: int, message: str) -> bool:
        """
        执行所有安全检查

        Args:
            group_id: 群号
            message: 要发送的消息

        Returns:
            True 如果所有检查通过，False 如果有任何检查失败
        """
        # 检查群是否被暂停
        if self.is_group_paused(group_id):
            logger.warning(f"群 {group_id} 服务已暂停，拒绝发送消息")
            return False

        # 检查消息长度
        if not self.check_message_length(message):
            self.handle_violation(group_id, "length")
            return False

        # 检查发送频率
        if not self.check_rate_limit(group_id):
            self.handle_violation(group_id, "rate")
            return False

        return True


# 全局安全限制器实例
security_limiter = SecurityLimiter()
